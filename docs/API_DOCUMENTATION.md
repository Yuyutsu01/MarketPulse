# 📡 MarketPulse AI REST API Specification

Complete reference for all REST API endpoints exposed by the **MarketPulse AI Enterprise Server**.

Base URL: `http://localhost:8001` or `http://localhost:8000`

---

## 1. Authentication & Multi-Tenancy (`/api/auth`)

### `POST /api/auth/register`
Registers a new user, auto-provisions an Organization and Workspace, and seeds sample campaign data.

* **Request Body** (`UserCreate`):
  ```json
  {
    "name": "Senior Analyst",
    "email": "analyst@company.com",
    "password": "securePassword123!",
    "organization_name": "Growth Media Corp"
  }
  ```
* **Response** (`201 Created` - `UserResponse`):
  ```json
  {
    "id": 1,
    "name": "Senior Analyst",
    "email": "analyst@company.com",
    "organization_id": 1,
    "role": "OWNER",
    "is_active": true,
    "created_at": "2026-08-24T12:00:00Z"
  }
  ```

---

### `POST /api/auth/login`
Authenticates user credentials and issues OAuth2 Bearer Access & Refresh Tokens.

* **Request** (`application/x-www-form-urlencoded`):
  - `username`: `analyst@company.com`
  - `password`: `securePassword123!`
* **Response** (`200 OK` - `Token`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

---

## 2. Campaigns & Data Ingestion (`/api/campaigns`)

### `GET /api/campaigns/`
Returns historical campaigns uploaded by the authenticated user.
* **Headers**: `Authorization: Bearer <access_token>`
* **Response** (`200 OK`): List of campaign objects.

### `POST /api/campaigns/upload`
Uploads CSV/Excel file, executes Data Quality Engine validation rules, inserts valid campaigns into PostgreSQL, and triggers model retraining.
* **Headers**: `Authorization: Bearer <access_token>`
* **Form-Data**: `file`: `<binary_file.csv>`

---

## 3. Analytics & Aggregations (`/api/analytics`)

### `GET /api/analytics/kpis`
Fetches database-side SQL aggregated KPIs.
* **Response** (`200 OK` - `KPIResponse`):
  ```json
  {
    "ctr": 2.45,
    "cpc": 1.33,
    "cpm": 32.50,
    "roi": 38.62,
    "conversion_rate": 4.12,
    "cac": 32.25,
    "total_spend": 417240.50,
    "total_conversions": 12929,
    "total_clicks": 313810,
    "total_impressions": 12808571,
    "total_revenue": 578380.20
  }
  ```

### `GET /api/analytics/charts`
Returns Timeseries, Platform Share, and Comparison chart datasets.

---

## 4. ML Prediction Sandbox (`/api/predict`)

### `POST /api/predict/`
Simulates a target marketing campaign configuration and predicts expected CTR, CVR, ROI, and normalized Success Score (0-99%).

* **Request Body** (`PredictionCreate`):
  ```json
  {
    "campaign_name": "Q3_Summer_Promo",
    "platform": "Instagram",
    "spend": 500.0,
    "device": "Mobile",
    "audience_age": "25-34",
    "geography": "US",
    "hour": 20
  }
  ```
* **Response** (`200 OK` - `PredictionResponse`):
  ```json
  {
    "id": 12,
    "user_id": 1,
    "campaign_name": "Q3_Summer_Promo",
    "platform": "Instagram",
    "spend": 500.0,
    "device": "Mobile",
    "audience_age": "25-34",
    "geography": "US",
    "hour": 20,
    "predicted_roi": 254.74,
    "success_score": 94.3,
    "expected_ctr": 4.635,
    "expected_conversion_rate": 5.057,
    "recommendations": "[\"This campaign configuration aligns perfectly with historical performance benchmarks. Ready to launch!\"]",
    "created_at": "2026-08-24T12:30:00Z"
  }
  ```

---

## 5. Decision Engine & Vector Search (`/api/v1`)

### `POST /api/v1/attribution`
Calculates channel revenue credit using First Touch, Last Touch, Linear, Time Decay, or Position-Based models.

* **Request Body**:
  ```json
  {
    "channels": ["Google Ads", "Facebook", "Instagram"],
    "total_conversion_value": 1000.0,
    "model": "position_based"
  }
  ```
* **Response**:
  ```json
  {
    "Google Ads": 400.0,
    "Facebook": 200.0,
    "Instagram": 400.0
  }
  ```

### `POST /api/v1/optimization`
Solves SLSQP constrained channel budget allocation.

* **Request Body**:
  ```json
  {
    "total_budget": 10000.0,
    "channel_historical_roi": {
      "Google Ads": 45.0,
      "Instagram": 35.0,
      "Facebook": 20.0
    },
    "min_channel_spend_pct": 0.10,
    "max_channel_spend_pct": 0.50
  }
  ```

### `GET /api/v1/search/semantic`
Performs tenant-isolated Qdrant vector search.
* **Query Parameters**: `query=high+roi+instagram+mobile&limit=5`
