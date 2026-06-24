# SubhaSankalpam - Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Git
- (Optional) Python 3.11+ for local development without Docker

## Quick Start (Docker)

### 1. Clone and configure

```bash
git clone https://github.com/sahithyanjali/SubhaSankalpam.git
cd SubhaSankalpam

# Copy environment file
cp backend/.env.example backend/.env
# Edit backend/.env with your settings (API keys, secret key, etc.)
```

### 2. Start all services

```bash
docker-compose up -d
```

This starts:
- **PostgreSQL 15** on port 5432
- **Redis 7** on port 6379
- **FastAPI backend** on port 8000
- **Nginx** on ports 80/443

### 3. Database migrations run automatically

The backend container runs `alembic upgrade head` on startup, which:
- Creates all 13 database tables
- Seeds subscription plans (Free, Silver, Gold, Platinum)
- Seeds 30 interest categories

### 4. Access the application

- **API Documentation (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Nginx Proxy**: http://localhost

## Database Setup (Manual)

If running without Docker:

```bash
# Install PostgreSQL 15 and Redis 7
# Create database
createdb subhasankalpam

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/subhasankalpam"
export DATABASE_SYNC_URL="postgresql://postgres:postgres@localhost:5432/subhasankalpam"
export REDIS_URL="redis://localhost:6379/0"

# Run migrations
cd backend
pip install -r requirements.txt
alembic upgrade head
```

## Migrations

### Check current migration status
```bash
cd backend
alembic current
```

### Apply all pending migrations
```bash
alembic upgrade head
```

### Rollback last migration
```bash
alembic downgrade -1
```

### Create a new migration
```bash
alembic revision --autogenerate -m "description of changes"
```

## Migration Files

| Revision | Description |
|----------|-------------|
| `001_initial` | Creates all 13 tables, enums, indexes, and constraints |
| `002_seed_data` | Seeds subscription plans and interest categories |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/subhasankalpam` |
| `DATABASE_SYNC_URL` | Sync PostgreSQL connection string (for Alembic) | `postgresql://postgres:postgres@localhost:5432/subhasankalpam` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key | (auto-generated in dev) |
| `GOOGLE_AI_API_KEY` | Google AI Studio (Gemini) API key | (optional) |
| `OPENAI_API_KEY` | OpenAI API key | (optional) |
| `OTP_SERVICE_URL` | OTP/SMS service URL | (optional) |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000,http://localhost:8080` |

## Production Deployment

### Docker Production Build

```bash
docker-compose -f docker-compose.yml up -d --build
```

### Cloud Deployment Options

**Fly.io (Recommended for quick deployment):**
```bash
cd backend
fly launch
fly secrets set DATABASE_URL="..." REDIS_URL="..." SECRET_KEY="..."
fly deploy
```

**Railway:**
- Connect GitHub repo
- Add PostgreSQL and Redis plugins
- Set environment variables
- Auto-deploys on push to main

**AWS/GCP/Azure:**
- Use Kubernetes manifests in `infrastructure/k8s/`
- Configure secrets via cloud provider's secret manager
- Set up managed PostgreSQL and Redis instances

## Monitoring

- **Health endpoint**: `GET /health` returns `{"status": "healthy"}`
- **Docker logs**: `docker-compose logs -f backend`
- **Database status**: `docker-compose exec db pg_isready`

## Troubleshooting

### Database connection issues
```bash
# Check if PostgreSQL is running
docker-compose ps db
# Check logs
docker-compose logs db
```

### Migration errors
```bash
# Check current state
docker-compose exec backend alembic current
# Force to specific revision
docker-compose exec backend alembic stamp head
```

### Reset database (development only)
```bash
docker-compose down -v  # Removes volumes
docker-compose up -d    # Recreates fresh database
```
