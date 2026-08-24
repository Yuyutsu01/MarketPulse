from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.auth import auth
from app.database.seed_data import seed_user_campaigns

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    """
    Registers a new analyst/user, provisions an Organization & Workspace, and seeds sample campaign data.
    """
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered"
        )

    # 1. Provision Organization & Workspace
    org_name = user_in.organization_name or f"{user_in.name}'s Organization"
    org_slug = org_name.lower().replace(" ", "-").replace("'", "")
    
    # Avoid slug collision
    existing_org = db.query(models.Organization).filter(models.Organization.slug == org_slug).first()
    if existing_org:
        org_slug = f"{org_slug}-{int(datetime.utcnow().timestamp())}"

    organization = models.Organization(name=org_name, slug=org_slug)
    db.add(organization)
    db.commit()
    db.refresh(organization)

    workspace = models.Workspace(
        organization_id=organization.id,
        name="Default Workspace",
        slug="default-workspace"
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
        
    # 2. Create User as Organization Owner
    hashed_pwd = auth.get_password_hash(user_in.password)
    new_user = models.User(
        organization_id=organization.id,
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_pwd,
        role="OWNER"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Map user to workspace
    ws_user = models.WorkspaceUser(
        workspace_id=workspace.id,
        user_id=new_user.id,
        role="OWNER"
    )
    db.add(ws_user)
    
    # Audit log entry
    audit = models.AuditLog(
        organization_id=organization.id,
        workspace_id=workspace.id,
        actor_id=new_user.id,
        action="USER_REGISTER",
        resource=f"User:{new_user.id}",
        ip_address=request.client.host if request.client else "127.0.0.1"
    )
    db.add(audit)
    db.commit()
    
    # Auto-seed sample campaigns scoped to workspace
    try:
        seed_user_campaigns(db, new_user.id, organization_id=organization.id, workspace_id=workspace.id)
    except Exception as e:
        print(f"Error seeding user data: {e}")
        
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates email & password credentials and issues JWT Access & Refresh Tokens.
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    
    # Write Audit Log
    audit = models.AuditLog(
        organization_id=user.organization_id,
        actor_id=user.id,
        action="USER_LOGIN",
        resource=f"User:{user.id}",
        ip_address=request.client.host if request.client else "127.0.0.1"
    )
    db.add(audit)
    db.commit()

    # Generate Access & Refresh tokens
    access_token = auth.create_access_token(data={"sub": user.email, "org_id": user.organization_id})
    refresh_token = auth.create_refresh_token(data={"sub": user.email, "org_id": user.organization_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    """
    Returns current authenticated user details and organization role context.
    """
    return current_user
