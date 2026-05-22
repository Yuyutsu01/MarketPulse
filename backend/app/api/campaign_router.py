import io
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
import pandas as pd
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.auth import auth
from app.ml.ml_service import train_user_model

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

@router.get("/", response_model=List[schemas.CampaignResponse])
def get_campaigns(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Campaign).filter(models.Campaign.user_id == current_user.id).order_by(models.Campaign.date.desc()).all()

@router.get("/template")
def download_template():
    # Define sample CSV template
    csv_header = "campaign_name,platform,spend,clicks,impressions,conversions,revenue,device,audience_age,geography,hour,date\n"
    csv_rows = [
        "Summer_Promo_FB,Facebook,150.0,120,4800,8,480.0,Mobile,25-34,US,19,2026-05-20",
        "Search_Brand_Google,Google Ads,320.5,85,2500,6,360.0,Desktop,35-44,UK,11,2026-05-21",
        "Reels_Fashion_IG,Instagram,95.0,90,5600,12,600.0,Mobile,18-24,CA,21,2026-05-21",
        "TrendingDance_TikTok,TikTok,80.0,110,9500,5,250.0,Mobile,18-24,US,17,2026-05-22"
    ]
    csv_content = csv_header + "\n".join(csv_rows)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=marketpulse_template.csv"}
    )

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_campaigns(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv") and not file.filename.endswith(".xlsx") and not file.filename.endswith(".xls"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a CSV or Excel file."
        )
        
    try:
        contents = await file.read()
        
        # Parse Excel or CSV
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing file: {str(e)}"
        )

    # Required columns
    required_cols = [
        "campaign_name", "platform", "spend", "clicks", 
        "impressions", "conversions", "device", 
        "audience_age", "geography", "hour", "date"
    ]
    
    # Check if columns exist
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns in upload: {', '.join(missing_cols)}"
        )
        
    campaigns_to_add = []
    
    # Process rows
    for idx, row in df.iterrows():
        try:
            # Parse and validate values
            camp_name = str(row["campaign_name"]).strip()
            platform = str(row["platform"]).strip()
            spend = float(row["spend"])
            clicks = int(row["clicks"])
            impressions = int(row["impressions"])
            conversions = int(row["conversions"])
            
            # Revenue optional
            revenue = float(row["revenue"]) if "revenue" in df.columns and not pd.isna(row["revenue"]) else None
            
            device = str(row["device"]).strip()
            audience_age = str(row["audience_age"]).strip()
            geography = str(row["geography"]).strip()
            hour = int(row["hour"])
            
            # Date parsing
            date_val = row["date"]
            if isinstance(date_val, str):
                date_parsed = datetime.strptime(date_val.strip(), "%Y-%m-%d").date()
            elif isinstance(date_val, (datetime, pd.Timestamp)):
                date_parsed = date_val.date()
            else:
                date_parsed = date_val
                
            # Basic validation check
            if spend < 0 or clicks < 0 or impressions < 0 or conversions < 0:
                raise ValueError("Metrics (spend, clicks, impressions, conversions) cannot be negative.")
            if hour < 0 or hour > 23:
                raise ValueError("Hour must be between 0 and 23.")
                
            campaign = models.Campaign(
                user_id=current_user.id,
                campaign_name=camp_name,
                platform=platform,
                spend=spend,
                clicks=clicks,
                impressions=impressions,
                conversions=conversions,
                revenue=revenue,
                device=device,
                audience_age=audience_age,
                geography=geography,
                hour=hour,
                date=date_parsed
            )
            campaigns_to_add.append(campaign)
            
        except Exception as row_error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Row {idx + 2} validation error: {str(row_error)}"
            )

    if not campaigns_to_add:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file does not contain any valid campaign data."
        )

    # Save to database
    try:
        db.add_all(campaigns_to_add)
        db.commit()
    except Exception as db_error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insert error: {str(db_error)}"
        )
        
    # Queue model retraining in background
    background_tasks.add_task(train_user_model, db, current_user.id)
    
    return {"message": f"Successfully uploaded {len(campaigns_to_add)} campaign records."}

@router.get("/{id}", response_model=schemas.CampaignResponse)
def get_campaign(
    id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(models.Campaign).filter(
        models.Campaign.id == id, 
        models.Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign

@router.delete("/{id}")
def delete_campaign(
    id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(models.Campaign).filter(
        models.Campaign.id == id,
        models.Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
        
    db.delete(campaign)
    db.commit()
    return {"message": "Campaign successfully deleted"}
