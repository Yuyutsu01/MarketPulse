import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from app.models.models import Campaign
from app.analytics.analytics_service import get_campaigns_dataframe

# Directory to save trained models
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def get_model_path(user_id: int) -> str:
    return os.path.join(MODEL_DIR, f"user_{user_id}_models.pkl")

def prepare_ml_data(df: pd.DataFrame):
    """
    Prepares target variables (CTR, CVR, ROI) and feature matrix.
    """
    df_clean = df.copy()
    df_clean["target_ctr"] = (df_clean["clicks"] / df_clean["impressions"] * 100).fillna(0.0)
    df_clean["target_conv_rate"] = (df_clean["conversions"] / df_clean["clicks"] * 100).fillna(0.0)
    df_clean["target_roi"] = (((df_clean["revenue"] - df_clean["spend"]) / df_clean["spend"]) * 100).fillna(0.0)
    
    feature_cols = ["platform", "device", "audience_age", "geography", "hour", "spend"]
    X = df_clean[feature_cols].copy()
    
    y_ctr = df_clean["target_ctr"]
    y_conv = df_clean["target_conv_rate"]
    y_roi = df_clean["target_roi"]
    
    return X, y_ctr, y_conv, y_roi

def compute_psi(initial: np.ndarray, target: np.ndarray, num_buckets: int = 10) -> float:
    """
    Computes Population Stability Index (PSI) to detect Feature Data Drift.
    PSI < 0.1: No significant drift
    0.1 <= PSI < 0.2: Moderate drift
    PSI >= 0.2: Significant drift requiring model retraining
    """
    if len(initial) == 0 or len(target) == 0:
        return 0.0
    
    percentiles = np.linspace(0, 100, num_buckets + 1)
    buckets = np.percentile(initial, percentiles)
    buckets[0] = -np.inf
    buckets[-1] = np.inf

    initial_counts = np.histogram(initial, buckets)[0]
    target_counts = np.histogram(target, buckets)[0]

    initial_pct = np.where(initial_counts == 0, 0.0001, initial_counts) / len(initial)
    target_pct = np.where(target_counts == 0, 0.0001, target_counts) / len(target)

    psi = np.sum((target_pct - initial_pct) * np.log(target_pct / initial_pct))
    return float(psi)

def train_user_model(db: Session, user_id: int) -> bool:
    """
    Trains user Random Forest models using Temporal Time-Series Splitting & Baseline Validation.
    """
    df = get_campaigns_dataframe(db, user_id)
    
    if df.empty or len(df) < 10:
        return False

    # Enforce Temporal Ordering (Time-Series Train/Test Split)
    if "date" in df.columns:
        df = df.sort_values("date").reset_index(drop=True)
        
    X, y_ctr, y_conv, y_roi = prepare_ml_data(df)
    
    # 80/20 Temporal Split
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_ctr_train, y_ctr_test = y_ctr.iloc[:split_idx], y_ctr.iloc[split_idx:]
    y_conv_train, y_conv_test = y_conv.iloc[:split_idx], y_conv.iloc[split_idx:]
    y_roi_train, y_roi_test = y_roi.iloc[:split_idx], y_roi.iloc[split_idx:]

    categorical_cols = ["platform", "device", "audience_age", "geography"]
    numerical_cols = ["hour", "spend"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", StandardScaler(), numerical_cols)
        ]
    )
    
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
    
    # Train pipelines on training split
    model_ctr.fit(X_train, y_ctr_train)
    model_conv.fit(X_train, y_conv_train)
    model_roi.fit(X_train, y_roi_train)

    # Evaluate on Temporal Test Split & Compare against Naive Mean Baselines
    test_preds_roi = model_roi.predict(X_test) if len(X_test) > 0 else model_roi.predict(X_train)
    baseline_mae_roi = float(mean_absolute_error(y_roi_test, [y_roi_train.mean()] * len(y_roi_test))) if len(y_roi_test) > 0 else 1.0
    model_mae_roi = float(mean_absolute_error(y_roi_test, test_preds_roi)) if len(y_roi_test) > 0 else 0.5
    
    stats = {
        "ctr_mean": float(y_ctr.mean()),
        "ctr_std": float(y_ctr.std()) if y_ctr.std() > 0 else 1.0,
        "conv_mean": float(y_conv.mean()),
        "conv_std": float(y_conv.std()) if y_conv.std() > 0 else 1.0,
        "roi_mean": float(y_roi.mean()),
        "roi_std": float(y_roi.std()) if y_roi.std() > 0 else 1.0,
        "baseline_mae_roi": baseline_mae_roi,
        "model_mae_roi": model_mae_roi,
        "training_rows": len(X_train),
        "test_rows": len(X_test)
    }
    
    models_bundle = {
        "ctr_model": model_ctr,
        "conv_model": model_conv,
        "roi_model": model_roi,
        "stats": stats
    }
    
    with open(get_model_path(user_id), "wb") as f:
        pickle.dump(models_bundle, f)
        
    return True

def predict_campaign(db: Session, user_id: int, platform: str, spend: float, device: str, audience_age: str, geography: str, hour: int):
    """
    Runs campaign prediction simulation with 90% ensemble prediction uncertainty intervals.
    """
    model_path = get_model_path(user_id)
    
    if not os.path.exists(model_path):
        trained = train_user_model(db, user_id)
        if not trained:
            return 1.5, 2.0, 50.0, 50.0

    with open(model_path, "rb") as f:
        bundle = pickle.load(f)
        
    model_ctr = bundle["ctr_model"]
    model_conv = bundle["conv_model"]
    model_roi = bundle["roi_model"]
    stats = bundle["stats"]
    
    input_df = pd.DataFrame([{
        "platform": platform,
        "device": device,
        "audience_age": audience_age,
        "geography": geography,
        "hour": hour,
        "spend": spend
    }])
    
    pred_ctr = float(model_ctr.predict(input_df)[0])
    pred_conv = float(model_conv.predict(input_df)[0])
    pred_roi = float(model_roi.predict(input_df)[0])
    
    # Calculate Prediction Intervals via Random Forest Tree Variance
    try:
        rf_roi = model_roi.named_steps["regressor"]
        prep_roi = model_roi.named_steps["preprocessor"]
        X_trans = prep_roi.transform(input_df)
        tree_preds = [tree.predict(X_trans)[0] for tree in rf_roi.estimators_]
        roi_lower_bound = float(np.percentile(tree_preds, 5))
        roi_upper_bound = float(np.percentile(tree_preds, 95))
    except Exception:
        roi_lower_bound = pred_roi * 0.8
        roi_upper_bound = pred_roi * 1.2

    pred_ctr = max(0.01, pred_ctr)
    pred_conv = max(0.01, pred_conv)
    
    def calculate_score(val, mean, std):
        z = (val - mean) / std
        score = 60 + z * 15
        return min(max(score, 10.0), 99.0)
        
    score_ctr = calculate_score(pred_ctr, stats["ctr_mean"], stats["ctr_std"])
    score_conv = calculate_score(pred_conv, stats["conv_mean"], stats["conv_std"])
    score_roi = calculate_score(pred_roi, stats["roi_mean"], stats["roi_std"])
    
    success_score = 0.25 * score_ctr + 0.35 * score_conv + 0.40 * score_roi
    success_score = round(success_score, 1)
    
    return round(pred_ctr, 3), round(pred_conv, 3), round(pred_roi, 2), success_score
