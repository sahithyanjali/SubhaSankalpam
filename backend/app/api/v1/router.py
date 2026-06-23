from fastapi import APIRouter

from app.api.v1.endpoints import admin, ai, auth, chat, horoscope, matches, notifications, photos, profiles, subscriptions

api_router = APIRouter()

# Module 1: User Portal
api_router.include_router(auth.router)
api_router.include_router(profiles.router)
api_router.include_router(horoscope.router)
api_router.include_router(photos.router)
api_router.include_router(matches.router)
api_router.include_router(chat.router)
api_router.include_router(notifications.router)
api_router.include_router(subscriptions.router)

# Module 2: Admin Operations
api_router.include_router(admin.router)

# Module 3: AI Intelligence
api_router.include_router(ai.router)
