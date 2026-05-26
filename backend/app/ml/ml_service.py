import os
import pickle
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from app.models.models import Campaign
from app.analytics.analytics_service import get_campaigns_dataframe

# Directory to save trained models
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def get_model_path(user_id: int) -> str:
    return os.path.join(MODEL_DIR, f"user_{user_id}_models.pkl")

def prepare_ml_data(df: pd.DataFrame):
    # Calculate target variables
    # CTR in %
    df["target_ctr"] = (df["clicks"] / df["impressions"] * 100).fillna(0.0)
    # Conversion Rate in %
    df["target_conv_rate"] = (df["conversions"] / df["clicks"] * 100).fillna(0.0)
    # ROI in %
    df["target_roi"] = (((df["revenue"] - df["spend"]) / df["spend"]) * 100).fillna(0.0)
    
    # Feature columns
    feature_cols = ["platform", "device", "audience_age", "geography", "hour", "spend"]
    X = df[feature_cols].copy()
    
    # Hour can be treated as numeric or categorical. Let's treat it as numeric for simplicity, or categorical.
    # We will treat hour as numeric but let's keep it in the feature space.
    y_ctr = df["target_ctr"]
    y_conv = df["target_conv_rate"]
    y_roi = df["target_roi"]
    
    return X, y_ctr, y_conv, y_roi

def train_user_model(db: Session, user_id: int) -> bool:
    df = get_campaigns_dataframe(db, user_id)
    
    # We need a reasonable amount of data to train a model. Let's say at least 10 rows.
    if df.empty or len(df) < 10:
        return False
        
    X, y_ctr, y_conv, y_roi = prepare_ml_data(df)
    
    # Categorical and numerical columns
    categorical_cols = ["platform", "device", "audience_age", "geography"]
    numerical_cols = ["hour", "spend"]
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", StandardScaler(), numerical_cols)
        ]
    )
    
    # Create pipelines for the 3 target variables
    # We use small estimators and depths to keep it fast and avoid overfitting on small datasets
    model_ctr = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42))
    ])
    
    model_conv = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42))
    ])
    
    model_roi = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42))
    ])
    
    # Train the pipelines
    model_ctr.fit(X, y_ctr)
    model_conv.fit(X, y_conv)
    model_roi.fit(X, y_roi)
    
    # Calculate target distribution parameters for success scoring normalization
    stats = {
        "ctr_mean": float(y_ctr.mean()),
        "ctr_std": float(y_ctr.std()) if y_ctr.std() > 0 else 1.0,
        "conv_mean": float(y_conv.mean()),
        "conv_std": float(y_conv.std()) if y_conv.std() > 0 else 1.0,
        "roi_mean": float(y_roi.mean()),
        "roi_std": float(y_roi.std()) if y_roi.std() > 0 else 1.0
    }
    
    # Bundle models and stats
    models_bundle = {
        "ctr_model": model_ctr,
        "conv_model": model_conv,
        "roi_model": model_roi,
        "stats": stats
    }
    
    # Save bundle
    with open(get_model_path(user_id), "wb") as f:
        pickle.dump(models_bundle, f)
        
    return True

def predict_campaign(db: Session, user_id: int, platform: str, spend: float, device: str, audience_age: str, geography: str, hour: int):
    model_path = get_model_path(user_id)
    
    # If model doesn't exist, try training it first
    if not os.path.exists(model_path):
        trained = train_user_model(db, user_id)
        if not trained:
            # Return baseline averages if we can't train
            return 1.5, 2.0, 50.0, 50.0 # defaults: ctr, conv_rate, roi, success
            
    # Load model bundle
    with open(model_path, "rb") as f:
        bundle = pickle.load(f)
        
    model_ctr = bundle["ctr_model"]
    model_conv = bundle["conv_model"]
    model_roi = bundle["roi_model"]
    stats = bundle["stats"]
    
    # Prepare single row dataframe for prediction
    input_df = pd.DataFrame([{
        "platform": platform,
        "device": device,
        "audience_age": audience_age,
        "geography": geography,
        "hour": hour,
        "spend": spend
    }])
    
    # Predictions
    pred_ctr = float(model_ctr.predict(input_df)[0])
    pred_conv = float(model_conv.predict(input_df)[0])
    pred_roi = float(model_roi.predict(input_df)[0])
    
    # Post-process predictions (ensure no negative values for CTR and Conv rate)
    pred_ctr = max(0.01, pred_ctr)
    pred_conv = max(0.01, pred_conv)
    
    # Calculate Success Score (0 to 100)
    # Success is defined as how much better the campaign is expected to perform
    # compared to the user's historical average.
    # Normalize scores: (pred - mean) / std -> convert to percentile or 0-100 range.
    def calculate_score(val, mean, std):
        z = (val - mean) / std
        # Map z-score (-2 to +2) to range 30 to 90
        score = 60 + z * 15
        return min(max(score, 10.0), 99.0) # bound between 10% and 99%
        
    score_ctr = calculate_score(pred_ctr, stats["ctr_mean"], stats["ctr_std"])
    score_conv = calculate_score(pred_conv, stats["conv_mean"], stats["conv_std"])
    score_roi = calculate_score(pred_roi, stats["roi_mean"], stats["roi_std"])
    
    # Success score is a weighted average of the subscores
    success_score = 0.25 * score_ctr + 0.35 * score_conv + 0.40 * score_roi
    success_score = round(success_score, 1)
    
    return round(pred_ctr, 3), round(pred_conv, 3), round(pred_roi, 2), success_score
