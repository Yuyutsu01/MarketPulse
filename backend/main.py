import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.database import engine, Base
from app.api import auth_router, campaign_router, analytics_router, predict_router, enterprise_router

# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MarketPulse AI Enterprise API",
    description="Enterprise Marketing Intelligence, Prediction, Attribution, Experimentation, and Budget Optimization Engine",
    version="2.0.0"
)

# Configure CORS securely from settings
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex="https?://.*" if settings.ENVIRONMENT == "development" else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router.router)
app.include_router(campaign_router.router)
app.include_router(analytics_router.router)
app.include_router(predict_router.router)
app.include_router(enterprise_router.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "MarketPulse AI Enterprise API",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "auth": "/api/auth",
            "campaigns": "/api/campaigns",
            "analytics": "/api/analytics",
            "predictions": "/api/predict",
            "enterprise_v1": "/api/v1"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

