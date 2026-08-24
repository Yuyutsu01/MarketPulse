from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import models
from app.auth import auth
from app.services.attribution_service import MultiTouchAttributionEngine
from app.services.experimentation_service import ExperimentationEngine
from app.services.optimization_service import BudgetOptimizationEngine
from app.services.qdrant_service import qdrant_service

router = APIRouter(prefix="/api/v1", tags=["enterprise"])

# Request / Response Schemas
class AttributionRequest(BaseModel):
    channels: List[str]
    total_conversion_value: float = Field(..., gt=0)
    model: str = "linear"  # first_touch, last_touch, linear, position_based, time_decay

class ExperimentRequest(BaseModel):
    control_conversions: int = Field(..., ge=0)
    control_sample_size: int = Field(..., gt=0)
    treatment_conversions: int = Field(..., ge=0)
    treatment_sample_size: int = Field(..., gt=0)
    confidence_level: float = 0.95

class BudgetOptimizeRequest(BaseModel):
    total_budget: float = Field(..., gt=0)
    channel_historical_roi: Dict[str, float]
    min_channel_spend_pct: float = 0.05
    max_channel_spend_pct: float = 0.50

@router.post("/attribution")
def calculate_attribution(
    payload: AttributionRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Computes Multi-Touch Marketing Attribution credit across channels.
    """
    try:
        return MultiTouchAttributionEngine.calculate_attribution(
            channels=payload.channels,
            total_conversion_value=payload.total_conversion_value,
            model=payload.model
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/experimentation")
def analyze_experiment(
    payload: ExperimentRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Calculates A/B test percentage lift, z-score, p-value, 95% confidence intervals, and significance.
    """
    try:
        return ExperimentationEngine.analyze_experiment(
            control_conversions=payload.control_conversions,
            control_sample_size=payload.control_sample_size,
            treatment_conversions=payload.treatment_conversions,
            treatment_sample_size=payload.treatment_sample_size,
            confidence_level=payload.confidence_level
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/optimization")
def optimize_budget(
    payload: BudgetOptimizeRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Solves optimal channel budget allocation using SLSQP optimization under constraints.
    """
    try:
        return BudgetOptimizationEngine.optimize_budget(
            total_budget=payload.total_budget,
            channel_historical_roi=payload.channel_historical_roi,
            min_channel_spend_pct=payload.min_channel_spend_pct,
            max_channel_spend_pct=payload.max_channel_spend_pct
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search/semantic")
def search_semantic(
    query: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=20),
    current_user: models.User = Depends(auth.get_current_user),
    workspace: models.Workspace = Depends(auth.get_current_workspace)
):
    """
    Performs tenant-isolated vector semantic search over campaign knowledge using Qdrant.
    """
    try:
        return qdrant_service.search_similar_campaigns(
            workspace_id=workspace.id,
            query_text=query,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search error: {str(e)}")

@router.get("/jobs/{job_id}")
def get_job_status(
    job_id: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves status and results for asynchronous background jobs.
    """
    job = db.query(models.JobStatus).filter(models.JobStatus.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job ID not found")
    return job
