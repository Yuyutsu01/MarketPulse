from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaigns = relationship("Campaign", back_populates="owner", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="owner", cascade="all, delete-orphan")

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    campaign_name = Column(String, nullable=False)
    platform = Column(String, nullable=False)  # Facebook, Google Ads, Instagram, TikTok, YouTube, etc.
    spend = Column(Float, nullable=False)
    clicks = Column(Integer, nullable=False)
    impressions = Column(Integer, nullable=False)
    conversions = Column(Integer, nullable=False)
    revenue = Column(Float, nullable=True)  # Optional revenue column for precise ROI
    device = Column(String, nullable=False)  # Mobile, Desktop, Tablet
    audience_age = Column(String, nullable=False)  # 18-24, 25-34, 35-44, 45-54, 55+
    geography = Column(String, nullable=False)  # US, UK, CA, AU, etc.
    hour = Column(Integer, nullable=False)  # 0 to 23
    date = Column(Date, nullable=False)  # Date of performance
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="campaigns")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    campaign_name = Column(String, nullable=True)
    platform = Column(String, nullable=False)
    spend = Column(Float, nullable=False)
    device = Column(String, nullable=False)
    audience_age = Column(String, nullable=False)
    geography = Column(String, nullable=False)
    hour = Column(Integer, nullable=False)
    
    predicted_roi = Column(Float, nullable=False)
    success_score = Column(Float, nullable=False)  # 0 to 100
    expected_conversion_rate = Column(Float, nullable=False)
    recommendations = Column(String, nullable=True)  # JSON or text field for generated tips
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="predictions")
