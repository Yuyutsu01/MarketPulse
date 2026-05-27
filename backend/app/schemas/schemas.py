from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List, Dict, Any

# Authentication Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Campaign Schemas
class CampaignBase(BaseModel):
    campaign_name: str
    platform: str
    spend: float = Field(..., gt=0)
    clicks: int = Field(..., ge=0)
    impressions: int = Field(..., ge=0)
    conversions: int = Field(..., ge=0)
    revenue: Optional[float] = Field(None, ge=0)
    device: str
    audience_age: str
    geography: str
    hour: int = Field(..., ge=0, le=23)
    date: date

class CampaignCreate(CampaignBase):
    pass

class CampaignResponse(CampaignBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Prediction Schemas
class PredictionBase(BaseModel):
    campaign_name: Optional[str] = None
    platform: str
    spend: float = Field(..., gt=0)
    device: str
    audience_age: str
    geography: str
    hour: int = Field(..., ge=0, le=23)

class PredictionCreate(PredictionBase):
    pass

class PredictionResponse(PredictionBase):
    id: int
    user_id: int
    predicted_roi: float
    success_score: float
    expected_conversion_rate: float
    recommendations: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics Response Schemas
class KPIResponse(BaseModel):
    ctr: float  # Click-Through Rate (%)
    cpc: float  # Cost Per Click ($)
    cpm: float  # Cost Per Mille ($)
    roi: float  # Return on Investment (%)
    conversion_rate: float  # Conversion Rate (%)
    cac: float  # Customer Acquisition Cost ($)
    total_spend: float
    total_conversions: int
    total_clicks: int
    total_impressions: int
    total_revenue: float

class TimeseriesData(BaseModel):
    date: str
    spend: float
    conversions: int
    clicks: int
    impressions: int
    revenue: float
    roi: float
    ctr: float

class PlatformShare(BaseModel):
    platform: str
    spend: float
    conversions: int
    clicks: int
    revenue: float
    roi: float

class PlatformComparison(BaseModel):
    platform: str
    ctr: float
    cpc: float
    conversion_rate: float
    roi: float

class DashboardChartsResponse(BaseModel):
    timeseries: List[TimeseriesData]
    platform_shares: List[PlatformShare]
    platform_comparisons: List[PlatformComparison]

class DeviceMetric(BaseModel):
    device: str
    spend: float
    conversions: int
    conversion_rate: float
    ctr: float
    cpc: float

class AgeMetric(BaseModel):
    age_group: str
    spend: float
    conversions: int
    conversion_rate: float
    cpc: float

class GeoMetric(BaseModel):
    geography: str
    spend: float
    conversions: int
    conversion_rate: float
    cac: float

class HourMetric(BaseModel):
    hour: int
    conversions: int
    conversion_rate: float

class AudienceInsightsResponse(BaseModel):
    devices: List[DeviceMetric]
    age_groups: List[AgeMetric]
    geography: List[GeoMetric]
    hourly_performance: List[HourMetric]
