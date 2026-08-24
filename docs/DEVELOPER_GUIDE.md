# 🛠️ MarketPulse AI Developer Guide

Welcome to the **MarketPulse AI Developer Guide**. This document provides code structure walkthroughs, local environment setup instructions, and testing guidelines.

---

## 1. Repository Structure

```text
MarketPulse/
├── assets/                       # Brand graphics and MarketPulse.png logo
├── docs/                         # System architecture, API specs, and deployment guides
├── docker-compose.yml            # Container orchestration specification
├── backend/                      # FastAPI Python Application
│   ├── app/
│   │   ├── analytics/            # SQL Aggregation & Recommendation Services
│   │   ├── api/                  # FastAPI APIRouter endpoints
│   │   ├── auth/                 # Bcrypt Hashing, JWT Tokens & RBAC
│   │   ├── core/                 # Pydantic BaseSettings management
│   │   ├── database/             # SQLAlchemy Engine & Seed Data Generator
│   │   ├── ml/                   # Scikit-Learn Random Forest pipelines & models
│   │   ├── models/               # SQLAlchemy Multi-Tenant ORM Entities
│   │   ├── schemas/              # Pydantic v2 Request/Response Schemas
│   │   ├── services/             # Attribution, Experimentation, Optimization & Qdrant Services
│   │   └── workers/              # Celery Async Background Tasks
│   ├── Dockerfile
│   ├── main.py                   # FastAPI Application Entry Point
│   ├── requirements.txt
│   └── test_backend.py           # Verification Test Suite
└── frontend/                     # React Vite SPA Application
    ├── public/                   # Static assets & favicons
    ├── src/
    │   ├── assets/               # Brand assets and images
    │   ├── components/           # Reusable UI components (Sidebar, KpiCard)
    │   ├── pages/                # Views (Dashboard, Predictions, Analytics, Upload)
    │   └── services/             # Axios API client
    ├── Dockerfile
    ├── index.html
    └── package.json
```

---

## 2. Running Local Verification Test Suite

Verify all database engines, multi-tenant models, bcrypt hashing, analytics aggregations, Random Forest ML training, and decision services:

```bash
# In the backend directory with active venv:
python test_backend.py
```

### What `test_backend.py` Validates

1. **DB Schema Initialization**: Drops and creates SQLite/PostgreSQL tables.
2. **Multi-Tenant Models**: Creates Organization, Workspace, User, and WorkspaceUser.
3. **Password Hashing**: Hashes and verifies password with bcrypt.
4. **Data Seeding**: Generates ~900 realistic campaign records across platforms.
5. **SQL Aggregations**: Calculates ROI, CTR, CPC, CAC, and CPM.
6. **ML Training**: Fits Random Forest Regressors and saves `user_1_models.pkl`.
7. **Predictor Simulation**: Executes prediction simulation query.
8. **Recommendation Engine**: Generates optimization advice.

---

## 3. Frontend Development Workflow

1. Navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Run Vite dev server with hot reload:
   ```bash
   npm run dev
   ```
4. Build production distribution:
   ```bash
   npm run build
   ```
