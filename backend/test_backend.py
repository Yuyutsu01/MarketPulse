import sys
import os
import shutil

# Ensure python knows where backend is
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database.database import engine, SessionLocal, Base
from app.models import models
from app.auth import auth
from app.database.seed_data import seed_user_campaigns
from app.analytics import analytics_service, recommendation_service
from app.ml import ml_service

def run_tests():
    print("=========================================")
    print("STAGING MARKETPULSE AI BACKEND VERIFICATION")
    print("=========================================")
    
    # 1. Clean and Setup Test Database
    print("\n1. Initializing DB and creating tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] DB Schema created.")

    db = SessionLocal()
    try:
        # 2. Test User Creation
        print("\n2. Testing User Creation...")
        test_email = "test@company.com"
        test_password = "password123"
        hashed = auth.get_password_hash(test_password)
        
        user = models.User(
            name="Test Analyst",
            email=test_email,
            hashed_password=hashed
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"[SUCCESS] Created User: ID={user.id}, Name={user.name}")
        
        # Verify Auth Hashing Check
        assert auth.verify_password(test_password, user.hashed_password) is True
        print("[SUCCESS] Password authentication verified.")

        # 3. Test Campaign Seeding
        print("\n3. Seeding Campaign Data (~900 items)...")
        seed_user_campaigns(db, user.id)
        
        campaigns_count = db.query(models.Campaign).filter(models.Campaign.user_id == user.id).count()
        print(f"[SUCCESS] Seeded {campaigns_count} campaigns in DB.")
        assert campaigns_count > 800

        # 4. Test Analytics Service
        print("\n4. Calculating KPIs & Chart aggregations...")
        kpis = analytics_service.calculate_kpis(db, user.id)
        print(f" - ROI: {kpis.roi}%")
        print(f" - CTR: {kpis.ctr}%")
        print(f" - CPC: ${kpis.cpc}")
        print(f" - Conversions: {kpis.total_conversions}")
        assert kpis.total_spend > 0
        assert kpis.total_conversions > 0
        print("[SUCCESS] KPIs calculated successfully.")
        
        charts = analytics_service.generate_dashboard_charts(db, user.id)
        print(f" - Timeseries points: {len(charts.timeseries)}")
        print(f" - Platform Share records: {len(charts.platform_shares)}")
        print(f" - Platform Comparison records: {len(charts.platform_comparisons)}")
        assert len(charts.timeseries) > 0
        assert len(charts.platform_shares) > 0
        print("[SUCCESS] Charts datasets created successfully.")

        # 5. Test ML Model Training
        print("\n5. Training Random Forest Regressor Model...")
        trained = ml_service.train_user_model(db, user.id)
        print(f" - Model training status: {trained}")
        assert trained is True
        
        model_path = ml_service.get_model_path(user.id)
        assert os.path.exists(model_path) is True
        print(f"[SUCCESS] Model successfully trained and saved to: {model_path}")

        # 6. Test Campaign Success Predictor
        print("\n6. Running Campaign Success Simulation...")
        ctr, cvr, roi, score = ml_service.predict_campaign(
            db=db,
            user_id=user.id,
            platform="Instagram",
            spend=500.0,
            device="Mobile",
            audience_age="25-34",
            geography="US",
            hour=20
        )
        print(f" - Simulation Output:")
        print(f"   * Expected CTR: {ctr}%")
        print(f"   * Expected CVR: {cvr}%")
        print(f"   * Expected ROI: {roi}%")
        print(f"   * Success Score: {score}/100")
        assert 0 <= score <= 100
        assert ctr > 0
        assert cvr > 0
        print("[SUCCESS] Simulation predict query succeeded.")

        # 7. Test Account Recommendation Engine
        print("\n7. Generating account optimization advice...")
        recs = recommendation_service.generate_recommendations(db, user.id)
        print(f" - Budget tips count: {len(recs['budget_allocation'])}")
        print(f" - Timing tips count: {len(recs['timing_optimization'])}")
        print(f" - Demographic tips count: {len(recs['demographic_insights'])}")
        print(f" - creative tips count: {len(recs['ad_performance'])}")
        assert len(recs['budget_allocation']) > 0
        print("[SUCCESS] Recommendations compiled.")
        
        print("\n=========================================")
        print("ALL BACKEND PIPELINES VERIFIED SUCCESSFULLY!")
        print("=========================================")
        
    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
