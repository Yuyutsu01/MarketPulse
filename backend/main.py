import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base
from app.api import auth_router, campaign_router, analytics_router, predict_router

# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MarketPulse AI API",
    description="AI-Powered Marketing Analytics and Campaign Success Prediction Engine",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router.router)
app.include_router(campaign_router.router)
app.include_router(analytics_router.router)
app.include_router(predict_router.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "MarketPulse AI API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "campaigns": "/api/campaigns",
            "analytics": "/api/analytics",
            "predictions": "/api/predict"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
