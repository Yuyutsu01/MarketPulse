# 🚀 MarketPulse AI Production Deployment Guide

This guide details how to deploy the **MarketPulse AI Enterprise Platform** to production environments using Docker Compose, PostgreSQL 16, Redis 7, Qdrant, and Nginx.

---

## 1. Production Architecture Overview

The system runs as 6 isolated containers connected via an internal bridge network `marketpulse_default`:

1. **`marketpulse_postgres`**: PostgreSQL 16 relational database with connection pooling.
2. **`marketpulse_redis`**: Redis 7 cache and Celery task broker.
3. **`marketpulse_qdrant`**: Qdrant vector search engine.
4. **`marketpulse_backend`**: FastAPI application server.
5. **`marketpulse_worker`**: Celery async worker instance.
6. **`marketpulse_frontend`**: Nginx web server serving compiled React SPA bundle.

---

## 2. Environment Configuration (`backend/.env`)

Before deploying to production, generate secure environment variables in `backend/.env`:

```ini
# Environment Mode
ENVIRONMENT=production

# Database Configuration
DATABASE_URL=postgresql://marketpulse:your_secure_password@postgres:5432/marketpulse_db

# Security & Secrets
JWT_SECRET_KEY=generate_a_long_random_64_character_hex_string_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=14

# Infrastructure Connections
REDIS_URL=redis://redis:6379/0
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# CORS Whitelist Configuration
CORS_ORIGINS=https://marketpulse.yourcompany.com,http://localhost:8080
```

---

## 3. Docker Compose Deployment

Launch the complete container stack:

```bash
docker compose up -d --build
```

### Checking Container Health

```bash
docker compose ps
```

Expected Output:
```text
NAME                   IMAGE                        STATUS
marketpulse_backend    marketpulse-backend          Up
marketpulse_frontend   marketpulse-frontend         Up (port 8080->80)
marketpulse_postgres   postgres:16-alpine           Up (healthy)
marketpulse_qdrant     qdrant/qdrant:latest         Up
marketpulse_redis      redis:7-alpine               Up
marketpulse_worker     marketpulse-celery_worker    Up
```

---

## 4. Reverse Proxy & SSL Setup (Nginx / Certbot)

For internet-facing production deployments, route traffic through a host-level Nginx reverse proxy with SSL termination:

```nginx
server {
    listen 443 ssl http2;
    server_name marketpulse.yourcompany.com;

    ssl_certificate /etc/letsencrypt/live/marketpulse.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/marketpulse.yourcompany.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 5. Monitoring & Backup

- **Database Backup**:
  ```bash
  docker exec -t marketpulse_postgres pg_dump -U marketpulse marketpulse_db > backup_$(date +%F).sql
  ```
- **Container Logs**:
  ```bash
  docker compose logs -f backend celery_worker
  ```
