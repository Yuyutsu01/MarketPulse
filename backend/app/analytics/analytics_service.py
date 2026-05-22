import pandas as pd
from sqlalchemy.orm import Session
from app.models.models import Campaign
from app.schemas.schemas import (
    KPIResponse, DashboardChartsResponse, AudienceInsightsResponse,
    TimeseriesData, PlatformShare, PlatformComparison,
    DeviceMetric, AgeMetric, GeoMetric, HourMetric
)

def get_campaigns_dataframe(db: Session, user_id: int) -> pd.DataFrame:
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

def calculate_kpis(db: Session, user_id: int) -> KPIResponse:
    df = get_campaigns_dataframe(db, user_id)
    
    if df.empty:
        return KPIResponse(
            ctr=0.0, cpc=0.0, cpm=0.0, roi=0.0, conversion_rate=0.0, cac=0.0,
            total_spend=0.0, total_conversions=0, total_clicks=0, total_impressions=0, total_revenue=0.0
        )
        
    total_spend = float(df["spend"].sum())
    total_clicks = int(df["clicks"].sum())
    total_impressions = int(df["impressions"].sum())
    total_conversions = int(df["conversions"].sum())
    total_revenue = float(df["revenue"].sum())

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
    df = get_campaigns_dataframe(db, user_id)
    
    if df.empty:
        return DashboardChartsResponse(timeseries=[], platform_shares=[], platform_comparisons=[])
        
    # 1. Timeseries (grouped by Date)
    df["date_str"] = df["date"].astype(str)
    ts_grouped = df.groupby("date_str").agg({
        "spend": "sum",
        "conversions": "sum",
        "clicks": "sum",
        "impressions": "sum",
        "revenue": "sum"
    }).reset_index().sort_values("date_str")
    
    timeseries = []
    for _, row in ts_grouped.iterrows():
        spend = float(row["spend"])
        revenue = float(row["revenue"])
        clicks = int(row["clicks"])
        impressions = int(row["impressions"])
        
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0.0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        
        timeseries.append(TimeseriesData(
            date=row["date_str"],
            spend=round(spend, 2),
            conversions=int(row["conversions"]),
            clicks=clicks,
            impressions=impressions,
            revenue=round(revenue, 2),
            roi=round(roi, 2),
            ctr=round(ctr, 2)
        ))
        
    # 2. Platform Shares (grouped by Platform)
    plat_grouped = df.groupby("platform").agg({
        "spend": "sum",
        "conversions": "sum",
        "clicks": "sum",
        "revenue": "sum"
    }).reset_index()
    
    platform_shares = []
    for _, row in plat_grouped.iterrows():
        spend = float(row["spend"])
        revenue = float(row["revenue"])
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0.0
        
        platform_shares.append(PlatformShare(
            platform=row["platform"],
            spend=round(spend, 2),
            conversions=int(row["conversions"]),
            clicks=int(row["clicks"]),
            revenue=round(revenue, 2),
            roi=round(roi, 2)
        ))

    # 3. Platform Comparisons (CTR, CPC, Conv Rate, ROI)
    plat_comp_grouped = df.groupby("platform").agg({
        "clicks": "sum",
        "impressions": "sum",
        "spend": "sum",
        "conversions": "sum",
        "revenue": "sum"
    }).reset_index()
    
    platform_comparisons = []
    for _, row in plat_comp_grouped.iterrows():
        clicks = int(row["clicks"])
        impressions = int(row["impressions"])
        spend = float(row["spend"])
        conversions = int(row["conversions"])
        revenue = float(row["revenue"])
        
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        cpc = (spend / clicks) if clicks > 0 else 0.0
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0.0
        
        platform_comparisons.append(PlatformComparison(
            platform=row["platform"],
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
    df = get_campaigns_dataframe(db, user_id)
    
    if df.empty:
        return AudienceInsightsResponse(devices=[], age_groups=[], geography=[], hourly_performance=[])
        
    # 1. Device Breakdown
    dev_grouped = df.groupby("device").agg({
        "spend": "sum",
        "conversions": "sum",
        "clicks": "sum",
        "impressions": "sum"
    }).reset_index()
    
    devices = []
    for _, row in dev_grouped.iterrows():
        clicks = int(row["clicks"])
        impressions = int(row["impressions"])
        spend = float(row["spend"])
        conversions = int(row["conversions"])
        
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        cpc = (spend / clicks) if clicks > 0 else 0.0
        
        devices.append(DeviceMetric(
            device=row["device"],
            spend=round(spend, 2),
            conversions=conversions,
            conversion_rate=round(conv_rate, 2),
            ctr=round(ctr, 2),
            cpc=round(cpc, 2)
        ))

    # 2. Age Group Breakdown
    age_grouped = df.groupby("audience_age").agg({
        "spend": "sum",
        "conversions": "sum",
        "clicks": "sum"
    }).reset_index()
    
    age_groups = []
    for _, row in age_grouped.iterrows():
        clicks = int(row["clicks"])
        spend = float(row["spend"])
        conversions = int(row["conversions"])
        
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
        cpc = (spend / clicks) if clicks > 0 else 0.0
        
        age_groups.append(AgeMetric(
            age_group=row["audience_age"],
            spend=round(spend, 2),
            conversions=conversions,
            conversion_rate=round(conv_rate, 2),
            cpc=round(cpc, 2)
        ))

    # 3. Geography Breakdown
    geo_grouped = df.groupby("geography").agg({
        "spend": "sum",
        "conversions": "sum",
        "clicks": "sum"
    }).reset_index()
    
    geography = []
    for _, row in geo_grouped.iterrows():
        clicks = int(row["clicks"])
        spend = float(row["spend"])
        conversions = int(row["conversions"])
        
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
        cac = (spend / conversions) if conversions > 0 else 0.0
        
        geography.append(GeoMetric(
            geography=row["geography"],
            spend=round(spend, 2),
            conversions=conversions,
            conversion_rate=round(conv_rate, 2),
            cac=round(cac, 2)
        ))

    # 4. Hourly Performance Breakdown
    hour_grouped = df.groupby("hour").agg({
        "conversions": "sum",
        "clicks": "sum"
    }).reset_index()
    
    hourly_performance = []
    for _, row in hour_grouped.iterrows():
        clicks = int(row["clicks"])
        conversions = int(row["conversions"])
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
        
        hourly_performance.append(HourMetric(
            hour=int(row["hour"]),
            conversions=conversions,
            conversion_rate=round(conv_rate, 2)
        ))
        
    return AudienceInsightsResponse(
        devices=devices,
        age_groups=age_groups,
        geography=geography,
        hourly_performance=hourly_performance
    )
