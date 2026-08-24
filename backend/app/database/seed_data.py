import random
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.models.models import Campaign, User, Organization, Workspace

def seed_user_campaigns(db: Session, user_id: int, organization_id: int = None, workspace_id: int = None):
    """
    Seeds realistic synthetic marketing campaign data (~900 items over 30 days) scoped to Organization & Workspace.
    """
    # Check if user already has campaigns
    existing_count = db.query(Campaign).filter(Campaign.user_id == user_id).count()
    if existing_count > 0:
        return

    # Fetch user if organization_id or workspace_id not passed
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        if not organization_id:
            organization_id = user.organization_id
        if not workspace_id and organization_id:
            workspace = db.query(Workspace).filter(Workspace.organization_id == organization_id).first()
            if workspace:
                workspace_id = workspace.id

    platforms = ["Facebook", "Google Ads", "Instagram", "TikTok", "YouTube"]
    devices = ["Mobile", "Desktop", "Tablet"]
    geographies = ["US", "UK", "CA", "AU", "DE"]
    age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]

    campaign_names = {
        "Facebook": ["FB_Lookalike_Purchasers", "FB_Retargeting_CartAbandoners", "FB_Prospecting_BroadInterest"],
        "Google Ads": ["Google_Brand_Search", "Google_Competitor_Keywords", "Google_Shopping_SmartFeed"],
        "Instagram": ["IG_Influencer_CoOp", "IG_Stories_SpringCollection", "IG_Reels_BrandAwareness"],
        "TikTok": ["TT_TrendingDance_Challenge", "TT_SparkAds_PromoCode", "TT_ProductDemo_Shorts"],
        "YouTube": ["YT_PreRoll_ExplainerVideo", "YT_Tutorial_Midroll", "YT_Unboxing_ReviewPartnership"]
    }

    # Generate data over the past 30 days
    today = date.today()
    campaign_records = []

    for day_offset in range(30):
        current_date = today - timedelta(days=day_offset)
        
        # Create 30 campaign records per day
        for _ in range(30):
            platform = random.choice(platforms)
            device = random.choice(devices)
            geo = random.choice(geographies)
            age = random.choice(age_groups)
            hour = random.randint(0, 23)
            
            campaign_name = random.choice(campaign_names[platform])
            
            # Base performance parameters based on channel to create realistic variations
            base_ctr = 0.02
            base_cpc = 1.0
            base_conv_rate = 0.02
            
            if platform == "Google Ads":
                base_ctr = 0.04
                base_cpc = 2.0
                base_conv_rate = 0.035
                if device == "Desktop":
                    base_conv_rate *= 1.3
                    base_ctr *= 1.2
            elif platform == "Instagram":
                base_ctr = 0.025
                base_cpc = 0.8
                base_conv_rate = 0.022
                if device == "Mobile":
                    base_ctr *= 1.4
                    base_conv_rate *= 1.4
                if 19 <= hour <= 22:
                    base_conv_rate *= 1.8
                    base_ctr *= 1.3
            elif platform == "TikTok":
                base_ctr = 0.015
                base_cpc = 0.5
                base_conv_rate = 0.015
                if age in ["18-24", "25-34"]:
                    base_conv_rate *= 1.6
                    base_ctr *= 1.5
                if device == "Mobile":
                    base_ctr *= 1.6
                if 16 <= hour <= 23:
                    base_conv_rate *= 1.4
            elif platform == "Facebook":
                base_ctr = 0.022
                base_cpc = 1.2
                base_conv_rate = 0.025
                if age in ["45-54", "55+"] and device == "Mobile":
                    base_conv_rate *= 0.4
                    base_ctr *= 0.6
            elif platform == "YouTube":
                base_ctr = 0.01
                base_cpc = 1.5
                base_conv_rate = 0.018
                if device == "Desktop":
                    base_conv_rate *= 1.2

            # Apply random noise
            ctr = base_ctr * random.uniform(0.8, 1.2)
            cpc = base_cpc * random.uniform(0.9, 1.1)
            conv_rate = base_conv_rate * random.uniform(0.8, 1.2)
            
            if geo == "US":
                cpc *= 1.2
                conv_rate *= 1.1
            elif geo == "DE":
                conv_rate *= 1.05
            elif geo == "CA":
                cpc *= 0.95

            is_weekend = (current_date.weekday() >= 5)
            budget_multiplier = 1.5 if is_weekend else 1.0
            
            impressions = int(random.randint(5000, 30000) * budget_multiplier)
            clicks = int(impressions * ctr)
            if clicks == 0:
                clicks = 1
                
            spend = round(clicks * cpc, 2)
            conversions = int(clicks * conv_rate)
            if conversions > clicks:
                conversions = clicks

            avg_order_value = random.uniform(40.0, 80.0)
            revenue = round(conversions * avg_order_value, 2)

            record = Campaign(
                organization_id=organization_id,
                workspace_id=workspace_id,
                user_id=user_id,
                campaign_name=campaign_name,
                platform=platform,
                spend=spend,
                clicks=clicks,
                impressions=impressions,
                conversions=conversions,
                revenue=revenue,
                device=device,
                audience_age=age,
                geography=geo,
                hour=hour,
                date=current_date
            )
            campaign_records.append(record)

    db.add_all(campaign_records)
    db.commit()
