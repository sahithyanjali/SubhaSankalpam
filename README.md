# SubhaSankalpam - AI-Powered Telugu Matrimony Platform

Production-ready matrimony platform built with Flutter Web, FastAPI, PostgreSQL, and AI-powered matching.

## Architecture

```
SubhaSankalpam/
├── backend/          # FastAPI Python Backend
├── frontend/         # Flutter Web Frontend
├── infrastructure/   # Docker, K8s, Nginx configs
├── docs/            # Architecture & API documentation
└── .github/         # CI/CD workflows
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Flutter Web, Material 3, Responsive Design |
| Backend | FastAPI (Python 3.11+), SQLAlchemy, Alembic |
| Database | PostgreSQL 15, Redis 7 |
| AI/ML | Google Gemini, OpenAI, LangChain, ChromaDB |
| Auth | JWT + OTP (Mobile & Email) |
| Infrastructure | Docker, Kubernetes, Nginx, GitHub Actions |

## Modules

1. **User Portal** - Registration, profiles, search, matching, chat, subscriptions
2. **Admin Operations** - Dashboard, moderation, reports, compliance
3. **AI Intelligence** - Fake detection, compatibility engine, recommendations, chat assistant

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
flutter pub get
flutter run -d chrome

# Docker (full stack)
docker-compose up --build
```

## Development Phases

- Phase 1: Database Schema
- Phase 2: Backend APIs
- Phase 3: Authentication
- Phase 4: Profile Module
- Phase 5: Matching Engine
- Phase 6: Chat System
- Phase 7: Admin Portal
- Phase 8: AI Services
- Phase 9: Deployment
