import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.auth import auth
from app.ml import ml_service
from app.analytics import recommendation_service

router = APIRouter(prefix="/api/predict", tags=["predictions"])

@router.post("/", response_model=schemas.PredictionResponse)
def run_prediction(
    prediction_in: schemas.PredictionCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Run ML prediction
    try:
        pred_ctr, pred_cvr, pred_roi, success_score = ml_service.predict_campaign(
            db=db,
            user_id=current_user.id,
            platform=prediction_in.platform,
            spend=prediction_in.spend,
            device=prediction_in.device,
            audience_age=prediction_in.audience_age,
            geography=prediction_in.geography,
            hour=prediction_in.hour
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction engine error: {str(e)}"
        )

    # Generate simulation-specific tips (what could be improved in this configuration)
    custom_tips = []
    
    # 1. Platform-specific suggestions
    if prediction_in.platform == "Instagram" and prediction_in.device == "Desktop":
        custom_tips.append("Instagram ads perform significantly better on **Mobile** devices. Switch targeting to Mobile to increase CVR.")
    if prediction_in.platform == "TikTok" and prediction_in.audience_age in ["45-54", "55+"]:
        custom_tips.append("TikTok's primary demographic is 18-34. Consider shifting this budget to **Facebook** or **Google Ads** for older audiences.")
        
    # 2. Timing warnings
    if prediction_in.platform == "Instagram" and not (19 <= prediction_in.hour <= 22):
        custom_tips.append("Instagram conversion rates peak between **7 PM and 10 PM**. Consider scheduling this ad run then.")
    if prediction_in.platform == "TikTok" and not (16 <= prediction_in.hour <= 23):
        custom_tips.append("TikTok engagement is highest in the late afternoon/evening (**4 PM - Midnight**). Adjust your campaign hours.")
        
    # 3. Demographic warnings
    if prediction_in.platform == "Facebook" and prediction_in.device == "Mobile" and prediction_in.audience_age in ["45-54", "55+"]:
        custom_tips.append("Facebook mobile users aged 45+ show historically low conversion efficiency. Audit targeting or use Desktop bids.")
        
    # 4. Budget warnings
    if prediction_in.spend > 2000 and prediction_in.platform == "TikTok":
        custom_tips.append("High single-day TikTok spend can lead to audience fatigue. Consider spreading this budget across 3-5 days.")
        
    if not custom_tips:
        custom_tips.append("This campaign configuration aligns perfectly with historical performance benchmarks. Ready to launch!")
        
    recommendations_str = json.dumps(custom_tips)

    # Save to predictions database table
    db_prediction = models.Prediction(
        user_id=current_user.id,
        campaign_name=prediction_in.campaign_name or "Simulation Run",
        platform=prediction_in.platform,
        spend=prediction_in.spend,
        device=prediction_in.device,
        audience_age=prediction_in.audience_age,
        geography=prediction_in.geography,
        hour=prediction_in.hour,
        predicted_roi=pred_roi,
        success_score=success_score,
        expected_conversion_rate=pred_cvr,
        recommendations=recommendations_str
    )
    
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction

@router.get("/history", response_model=List[schemas.PredictionResponse])
def get_prediction_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Prediction).filter(
        models.Prediction.user_id == current_user.id
    ).order_by(models.Prediction.created_at.desc()).limit(15).all()

@router.get("/recommendations")
def get_ai_recommendations(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Generates broad account-wide optimization insights based on historical records
    return recommendation_service.generate_recommendations(db, current_user.id)
