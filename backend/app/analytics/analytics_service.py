import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.models import Campaign
from app.schemas.schemas import (
    KPIResponse, DashboardChartsResponse, AudienceInsightsResponse,
    TimeseriesData, PlatformShare, PlatformComparison,
    DeviceMetric, AgeMetric, GeoMetric, HourMetric
)

def get_campaigns_dataframe(db: Session, user_id: int) -> pd.DataFrame:
    """
    Constructs a Pandas DataFrame from Campaign ORM records for ML feature extraction.
    """
    query = db.query(Campaign).filter(Campaign.user_id == user_id)
    campaigns = query.all()
    
    if not campaigns:
        return pd.DataFrame()
        
    data = []
    for c in campaigns:
        data.append({
            "id": c.id,
            "campaign_name": c.campaign_name,
            "platform": c.platform,
            "spend": c.spend,
            "clicks": c.clicks,
            "impressions": c.impressions,
            "conversions": c.conversions,
            "revenue": c.revenue if c.revenue is not None else 0.0,
            "device": c.device,
            "audience_age": c.audience_age,
            "geography": c.geography,
            "hour": c.hour,
            "date": c.date
        })
    return pd.DataFrame(data)

def ensure_user_data_seeded(db: Session, user_id: int):
    count = db.query(Campaign).filter(Campaign.user_id == user_id).count()
    if count == 0:
        from app.database.seed_data import seed_user_campaigns
        try:
            seed_user_campaigns(db, user_id)
        except Exception as e:
            print(f"Auto-seed error: {e}")

def calculate_kpis(db: Session, user_id: int) -> KPIResponse:
    """
    High-performance Database-Side SQL aggregation for main dashboard KPIs.
    """
    ensure_user_data_seeded(db, user_id)
    result = db.query(
        func.coalesce(func.sum(Campaign.spend), 0.0).label("total_spend"),
        func.coalesce(func.sum(Campaign.clicks), 0).label("total_clicks"),
        func.coalesce(func.sum(Campaign.impressions), 0).label("total_impressions"),
        func.coalesce(func.sum(Campaign.conversions), 0).label("total_conversions"),
        func.coalesce(func.sum(Campaign.revenue), 0.0).label("total_revenue")
    ).filter(Campaign.user_id == user_id).first()

    if not result or result.total_impressions == 0:
        return KPIResponse(
            ctr=0.0, cpc=0.0, cpm=0.0, roi=0.0, conversion_rate=0.0, cac=0.0,
            total_spend=0.0, total_conversions=0, total_clicks=0, total_impressions=0, total_revenue=0.0
        )

    total_spend = float(result.total_spend)
    total_clicks = int(result.total_clicks)
    total_impressions = int(result.total_impressions)
    total_conversions = int(result.total_conversions)
    total_revenue = float(result.total_revenue)

    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
    cpc = (total_spend / total_clicks) if total_clicks > 0 else 0.0
    cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0.0
    roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0.0
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0.0
    cac = (total_spend / total_conversions) if total_conversions > 0 else 0.0

    return KPIResponse(
        ctr=round(ctr, 2),
        cpc=round(cpc, 2),
        cpm=round(cpm, 2),
        roi=round(roi, 2),
        conversion_rate=round(conversion_rate, 2),
        cac=round(cac, 2),
        total_spend=round(total_spend, 2),
        total_conversions=total_conversions,
        total_clicks=total_clicks,
        total_impressions=total_impressions,
        total_revenue=round(total_revenue, 2)
    )

def generate_dashboard_charts(db: Session, user_id: int) -> DashboardChartsResponse:
    """
    Generates Timeseries, Platform Share, and Comparison chart datasets via SQL GroupBy.
    """
    ensure_user_data_seeded(db, user_id)
    # 1. Timeseries (Grouped by Date)
    ts_rows = db.query(
        Campaign.date,
        func.sum(Campaign.spend).label("spend"),
        func.sum(Campaign.conversions).label("conversions"),
        func.sum(Campaign.clicks).label("clicks"),
        func.sum(Campaign.impressions).label("impressions"),
        func.coalesce(func.sum(Campaign.revenue), 0.0).label("revenue")
    ).filter(Campaign.user_id == user_id).group_by(Campaign.date).order_by(Campaign.date.asc()).all()

    timeseries = []
    for row in ts_rows:
        spend = float(row.spend or 0.0)
        revenue = float(row.revenue or 0.0)
        clicks = int(row.clicks or 0)
        impressions = int(row.impressions or 0)
        
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0.0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        
        timeseries.append(TimeseriesData(
            date=str(row.date),
            spend=round(spend, 2),
            conversions=int(row.conversions or 0),
            clicks=clicks,
            impressions=impressions,
            revenue=round(revenue, 2),
            roi=round(roi, 2),
            ctr=round(ctr, 2)
        ))

    # 2. Platform Shares & Comparisons (Grouped by Platform)
    plat_rows = db.query(
        Campaign.platform,
        func.sum(Campaign.spend).label("spend"),
        func.sum(Campaign.conversions).label("conversions"),
        func.sum(Campaign.clicks).label("clicks"),
        func.sum(Campaign.impressions).label("impressions"),
        func.coalesce(func.sum(Campaign.revenue), 0.0).label("revenue")
    ).filter(Campaign.user_id == user_id).group_by(Campaign.platform).all()

    platform_shares = []
    platform_comparisons = []

    for row in plat_rows:
        spend = float(row.spend or 0.0)
        revenue = float(row.revenue or 0.0)
        clicks = int(row.clicks or 0)
        impressions = int(row.impressions or 0)
        conversions = int(row.conversions or 0)

        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0.0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        cpc = (spend / clicks) if clicks > 0 else 0.0
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0

        platform_shares.append(PlatformShare(
            platform=row.platform,
            spend=round(spend, 2),
            conversions=conversions,
            clicks=clicks,
            revenue=round(revenue, 2),
            roi=round(roi, 2)
        ))

        platform_comparisons.append(PlatformComparison(
            platform=row.platform,
            ctr=round(ctr, 2),
            cpc=round(cpc, 2),
            conversion_rate=round(conv_rate, 2),
            roi=round(roi, 2)
        ))

    return DashboardChartsResponse(
        timeseries=timeseries,
        platform_shares=platform_shares,
        platform_comparisons=platform_comparisons
    )

def generate_audience_insights(db: Session, user_id: int) -> AudienceInsightsResponse:
    """
    Generates Device, Age Cohort, Geography, and Hourly Insights using database-side GroupBy aggregations.
    """
    ensure_user_data_seeded(db, user_id)
    # 1. Devices Breakdown
    dev_rows = db.query(
        Campaign.device,
        func.sum(Campaign.spend).label("spend"),
        func.sum(Campaign.conversions).label("conversions"),
        func.sum(Campaign.clicks).label("clicks"),
        func.sum(Campaign.impressions).label("impressions")
    ).filter(Campaign.user_id == user_id).group_by(Campaign.device).all()

    devices = []
    for r in dev_rows:
        clicks = int(r.clicks or 0)
        impressions = int(r.impressions or 0)
        spend = float(r.spend or 0.0)
        conversions = int(r.conversions or 0)
        
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        cpc = (spend / clicks) if clicks > 0 else 0.0

        devices.append(DeviceMetric(
            device=r.device,
            spend=round(spend, 2),
            conversions=conversions,
            conversion_rate=round(conv_rate, 2),
            ctr=round(ctr, 2),
            cpc=round(cpc, 2)
        ))

    # 2. Age Group Breakdown
    age_rows = db.query(
        Campaign.audience_age,
        func.sum(Campaign.spend).label("spend"),
        func.sum(Campaign.conversions).label("conversions"),
        func.sum(Campaign.clicks).label("clicks")
    ).filter(Campaign.user_id == user_id).group_by(Campaign.audience_age).all()

    age_groups = []
    for r in age_rows:
        clicks = int(r.clicks or 0)
        spend = float(r.spend or 0.0)
        conversions = int(r.conversions or 0)
        
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
        cpc = (spend / clicks) if clicks > 0 else 0.0

        age_groups.append(AgeMetric(
            age_group=r.audience_age,
            spend=round(spend, 2),
            conversions=conversions,
            conversion_rate=round(conv_rate, 2),
            cpc=round(cpc, 2)
        ))

    # 3. Geography Breakdown
    geo_rows = db.query(
        Campaign.geography,
        func.sum(Campaign.spend).label("spend"),
        func.sum(Campaign.conversions).label("conversions"),
        func.sum(Campaign.clicks).label("clicks")
    ).filter(Campaign.user_id == user_id).group_by(Campaign.geography).all()

    geography = []
    for r in geo_rows:
        clicks = int(r.clicks or 0)
        spend = float(r.spend or 0.0)
        conversions = int(r.conversions or 0)
        
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
        cac = (spend / conversions) if conversions > 0 else 0.0

        geography.append(GeoMetric(
            geography=r.geography,
            spend=round(spend, 2),
            conversions=conversions,
            conversion_rate=round(conv_rate, 2),
            cac=round(cac, 2)
        ))

    # 4. Hourly Performance Breakdown
    hour_rows = db.query(
        Campaign.hour,
        func.sum(Campaign.conversions).label("conversions"),
        func.sum(Campaign.clicks).label("clicks")
    ).filter(Campaign.user_id == user_id).group_by(Campaign.hour).order_by(Campaign.hour.asc()).all()

    hourly_performance = []
    for r in hour_rows:
        clicks = int(r.clicks or 0)
        conversions = int(r.conversions or 0)
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0

        hourly_performance.append(HourMetric(
            hour=int(r.hour),
            conversions=conversions,
            conversion_rate=round(conv_rate, 2)
        ))

    return AudienceInsightsResponse(
        devices=devices,
        age_groups=age_groups,
        geography=geography,
        hourly_performance=hourly_performance
    )
