from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Organization(Base):
    """
    Top-level Multi-Tenant Organization boundary (e.g. Enterprise Client / Company).
    """
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspaces = relationship("Workspace", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")


class Workspace(Base):
    """
    Sub-boundary within an Organization (e.g. Brand, Region, Project Workspace).
    """
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="workspaces")
    workspace_users = relationship("WorkspaceUser", back_populates="workspace", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="workspace", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="workspace", cascade="all, delete-orphan")


class User(Base):
    """
    Authenticated Platform User with Multi-Tenant Organization and RBAC Role.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="ANALYST", nullable=False)  # OWNER, ADMIN, ANALYST, VIEWER
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")
    workspace_mappings = relationship("WorkspaceUser", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="owner", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="owner", cascade="all, delete-orphan")


class WorkspaceUser(Base):
    """
    Junction table mapping users to workspaces with specific roles.
    """
    __tablename__ = "workspace_users"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), default="ANALYST", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="workspace_users")
    user = relationship("User", back_populates="workspace_mappings")


class Campaign(Base):
    """
    Marketing Campaign record scoped to Workspace & Organization.
    """
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    campaign_name = Column(String(255), nullable=False)
    platform = Column(String(100), nullable=False, index=True)  # Facebook, Google Ads, Instagram, TikTok, YouTube, etc.
    spend = Column(Float, nullable=False)
    clicks = Column(Integer, nullable=False)
    impressions = Column(Integer, nullable=False)
    conversions = Column(Integer, nullable=False)
    revenue = Column(Float, nullable=True)
    device = Column(String(50), nullable=False)  # Mobile, Desktop, Tablet
    audience_age = Column(String(50), nullable=False)  # 18-24, 25-34, 35-44, 45-54, 55+
    geography = Column(String(50), nullable=False)  # US, UK, CA, AU, etc.
    hour = Column(Integer, nullable=False)  # 0 to 23
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="campaigns")
    owner = relationship("User", back_populates="campaigns")

    # Compound Indexes for high-performance workspace analytics filtering
    __table_args__ = (
        Index("idx_campaigns_workspace_date", "workspace_id", "date"),
        Index("idx_campaigns_workspace_platform", "workspace_id", "platform"),
    )


class Prediction(Base):
    """
    Machine Learning Campaign Prediction simulation record scoped to Workspace.
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    campaign_name = Column(String(255), nullable=True)
    platform = Column(String(100), nullable=False)
    spend = Column(Float, nullable=False)
    device = Column(String(50), nullable=False)
    audience_age = Column(String(50), nullable=False)
    geography = Column(String(50), nullable=False)
    hour = Column(Integer, nullable=False)
    
    predicted_roi = Column(Float, nullable=False)
    success_score = Column(Float, nullable=False)  # 0 to 100
    expected_ctr = Column(Float, nullable=True)
    expected_conversion_rate = Column(Float, nullable=False)
    recommendations = Column(Text, nullable=True)  # JSON formatted optimization tips
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    workspace = relationship("Workspace", back_populates="predictions")
    owner = relationship("User", back_populates="predictions")


class AuditLog(Base):
    """
    Enterprise Governance Audit Trail tracking user actions and security events.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action = Column(String(100), nullable=False)  # e.g., USER_LOGIN, CSV_UPLOAD, MODEL_TRAIN
    resource = Column(String(255), nullable=False)
    ip_address = Column(String(50), nullable=True)
    details_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    organization = relationship("Organization", back_populates="audit_logs")


class JobStatus(Base):
    """
    Async Celery Background Job Status tracking.
    """
    __tablename__ = "job_statuses"

    id = Column(String(255), primary_key=True, index=True)  # Celery Task ID
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    task_type = Column(String(100), nullable=False)  # e.g., CSV_UPLOAD, MODEL_TRAIN, EMBEDDING_GEN
    status = Column(String(50), default="QUEUED", nullable=False)  # QUEUED, RUNNING, SUCCESS, FAILED
    progress_percent = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    result_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataQualityReport(Base):
    """
    Ingestion Data Quality & Validation Score Audit Reports.
    """
    __tablename__ = "data_quality_reports"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_name = Column(String(255), nullable=False)
    total_rows = Column(Integer, nullable=False)
    valid_rows = Column(Integer, nullable=False)
    warning_rows = Column(Integer, default=0)
    rejected_rows = Column(Integer, default=0)
    issues_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
