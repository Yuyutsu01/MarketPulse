from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.auth import auth
from app.analytics import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/kpis", response_model=schemas.KPIResponse)
def get_kpis(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return analytics_service.calculate_kpis(db, current_user.id)

@router.get("/charts", response_model=schemas.DashboardChartsResponse)
def get_charts(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return analytics_service.generate_dashboard_charts(db, current_user.id)

@router.get("/audience", response_model=schemas.AudienceInsightsResponse)
def get_audience_insights(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return analytics_service.generate_audience_insights(db, current_user.id)
