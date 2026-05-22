import pandas as pd
from sqlalchemy.orm import Session
from app.analytics.analytics_service import get_campaigns_dataframe

def generate_recommendations(db: Session, user_id: int) -> dict:
    df = get_campaigns_dataframe(db, user_id)
    
    recommendations = {
        "budget_allocation": [],
        "timing_optimization": [],
        "demographic_insights": [],
        "ad_performance": []
    }
    
    if df.empty or len(df) < 5:
        recommendations["budget_allocation"].append("Upload more campaign data to unlock advanced AI-driven recommendations.")
        return recommendations
        
    # Calculate global metrics
    global_spend = df["spend"].sum()
    global_conversions = df["conversions"].sum()
    global_clicks = df["clicks"].sum()
    global_avg_cvr = (global_conversions / global_clicks * 100) if global_clicks > 0 else 0.0
    global_avg_ctr = (global_clicks / df["impressions"].sum() * 100) if df["impressions"].sum() > 0 else 0.0
    global_avg_cac = (global_spend / global_conversions) if global_conversions > 0 else 0.0

    # 1. Budget Allocation Tips
    # Group by platform to find ROI and conversion rates
    plat_stats = df.groupby("platform").agg({
        "spend": "sum",
        "conversions": "sum",
        "revenue": "sum"
    }).reset_index()
    
    plat_stats["roi"] = ((plat_stats["revenue"] - plat_stats["spend"]) / plat_stats["spend"] * 100).fillna(0.0)
    plat_stats["cac"] = (plat_stats["spend"] / plat_stats["conversions"]).fillna(0.0)
    
    if len(plat_stats) > 1:
        # Find best and worst ROI platforms
        best_plat = plat_stats.loc[plat_stats["roi"].idxmax()]
        worst_plat = plat_stats.loc[plat_stats["roi"].idxmin()]
        
        if best_plat["roi"] > worst_plat["roi"] + 15:  # At least 15% difference
            recommendations["budget_allocation"].append(
                f"Shift budget from **{worst_plat['platform']}** (ROI: {worst_plat['roi']:.1f}%) to "
                f"**{best_plat['platform']}** (ROI: {best_plat['roi']:.1f}%) to increase conversion efficiency."
            )
            
        # Find platform with highest Customer Acquisition Cost (CAC)
        high_cac_plat = plat_stats.loc[plat_stats["cac"].idxmax()]
        low_cac_plat = plat_stats.loc[plat_stats["cac"].idxmin()]
        if high_cac_plat["cac"] > low_cac_plat["cac"] * 1.5 and high_cac_plat["spend"] > 0.05 * global_spend:
            recommendations["budget_allocation"].append(
                f"Acquisition costs on **{high_cac_plat['platform']}** are high (${high_cac_plat['cac']:.2f}/conv vs. "
                f"${low_cac_plat['cac']:.2f}/conv on {low_cac_plat['platform']}). Consider capping spend here."
            )
            
    if not recommendations["budget_allocation"]:
        recommendations["budget_allocation"].append("Budget distribution is well-aligned with channel performance metrics.")

    # 2. Timing Optimization Tips
    # Group by platform and hour
    hour_stats = df.groupby(["platform", "hour"]).agg({
        "conversions": "sum",
        "clicks": "sum"
    }).reset_index()
    
    hour_stats["cvr"] = (hour_stats["conversions"] / hour_stats["clicks"] * 100).fillna(0.0)
    
    # Check for platform-specific peaks
    for plat in df["platform"].unique():
        plat_hours = hour_stats[hour_stats["platform"] == plat]
        if len(plat_hours) >= 3:
            best_hour_row = plat_hours.loc[plat_hours["cvr"].idxmax()]
            worst_hour_row = plat_hours.loc[plat_hours["cvr"].idxmin()]
            
            best_hour = int(best_hour_row["hour"])
            best_hour_cvr = best_hour_row["cvr"]
            
            # Format time
            time_ampm = f"{best_hour % 12 or 12} {'PM' if best_hour >= 12 else 'AM'}"
            time_window = f"{best_hour % 12 or 12} - {(best_hour + 2) % 12 or 12} {'PM' if best_hour >= 12 else 'AM'}"
            
            # Check if peak hour is significantly better than platform average
            plat_cvr = (df[df["platform"] == plat]["conversions"].sum() / df[df["platform"] == plat]["clicks"].sum() * 100)
            if best_hour_cvr > plat_cvr * 1.3:
                recommendations["timing_optimization"].append(
                    f"**{plat}** campaigns perform exceptionally well around **{time_ampm}** (Conversion Rate: {best_hour_cvr:.1f}% vs. "
                    f"average {plat_cvr:.1f}%). Schedule high-priority ads during this window."
                )

    if not recommendations["timing_optimization"]:
        recommendations["timing_optimization"].append("No significant time-of-day conversion variance detected. Standard scheduling is fine.")

    # 3. Demographic & Device Segments
    # Look at Age Groups
    age_stats = df.groupby("audience_age").agg({
        "spend": "sum",
        "conversions": "sum",
        "clicks": "sum"
    }).reset_index()
    age_stats["cvr"] = (age_stats["conversions"] / age_stats["clicks"] * 100).fillna(0.0)
    age_stats["cac"] = (age_stats["spend"] / age_stats["conversions"]).fillna(0.0)
    
    # Check for underperforming age group (CAC > 1.5 * average)
    underperforming_ages = age_stats[age_stats["cac"] > global_avg_cac * 1.4]
    for _, row in underperforming_ages.iterrows():
        if row["spend"] > 0.05 * global_spend: # Only flag if spend is material
            recommendations["demographic_insights"].append(
                f"Reduce spend on audience age segment **{row['audience_age']}** due to high Customer Acquisition Cost "
                f"(${row['cac']:.2f} compared to global average of ${global_avg_cac:.2f})."
            )

    # Look at Device Usage
    device_stats = df.groupby("device").agg({
        "spend": "sum",
        "conversions": "sum",
        "clicks": "sum"
    }).reset_index()
    device_stats["cvr"] = (device_stats["conversions"] / device_stats["clicks"] * 100).fillna(0.0)
    
    best_device = device_stats.loc[device_stats["cvr"].idxmax()]
    worst_device = device_stats.loc[device_stats["cvr"].idxmin()]
    
    if best_device["cvr"] > worst_device["cvr"] * 1.4:
        recommendations["demographic_insights"].append(
            f"**{best_device['device']}** users convert at a {best_device['cvr']:.1f}% rate, which is "
            f"significantly higher than **{worst_device['device']}** ({worst_device['cvr']:.1f}%). Adjust bids accordingly."
        )

    if not recommendations["demographic_insights"]:
        recommendations["demographic_insights"].append("Demographic and device performance profiles are stable and balanced.")

    # 4. Ad Creative & Funnel Optimization
    # Group by campaign name to find CTR and Conversion Rate issues
    camp_stats = df.groupby("campaign_name").agg({
        "impressions": "sum",
        "clicks": "sum",
        "conversions": "sum",
        "spend": "sum"
    }).reset_index()
    
    camp_stats["ctr"] = (camp_stats["clicks"] / camp_stats["impressions"] * 100).fillna(0.0)
    camp_stats["cvr"] = (camp_stats["conversions"] / camp_stats["clicks"] * 100).fillna(0.0)
    
    # Find campaigns with low CTR but high spend (low ad interest)
    low_ctr_camps = camp_stats[(camp_stats["ctr"] < global_avg_ctr * 0.7) & (camp_stats["spend"] > 0.05 * global_spend)]
    for _, row in low_ctr_camps.iterrows():
        recommendations["ad_performance"].append(
            f"Campaign **{row['campaign_name']}** has low click interest (CTR: {row['ctr']:.2f}% vs. average "
            f"{global_avg_ctr:.2f}%). Consider testing new ad copy, image assets, or targeting expansion."
        )
        
    # Find campaigns with high CTR but low conversion (landing page drop-off)
    leaky_funnels = camp_stats[(camp_stats["ctr"] > global_avg_ctr * 1.2) & (camp_stats["cvr"] < global_avg_cvr * 0.5) & (camp_stats["clicks"] > 20)]
    for _, row in leaky_funnels.iterrows():
        recommendations["ad_performance"].append(
            f"Campaign **{row['campaign_name']}** drives high traffic (CTR: {row['ctr']:.2f}%) but low checkouts "
            f"(CVR: {row['cvr']:.1f}%). Audit the landing page design, form friction, or promotional alignment."
        )
        
    if not recommendations["ad_performance"]:
        recommendations["ad_performance"].append("All individual campaigns exhibit healthy click-to-conversion funnel dynamics.")
        
    return recommendations
