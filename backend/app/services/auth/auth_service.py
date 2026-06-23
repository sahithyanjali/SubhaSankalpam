from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.user import User, UserStatus
from app.schemas.auth import TokenResponse


class AuthService:
    @staticmethod
    async def get_or_create_user_by_phone(
        db: AsyncSession, phone: str, profile_for: str = "myself"
    ) -> User:
        result = await db.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                phone=phone,
                is_phone_verified=True,
                status=UserStatus.ACTIVE,
                profile_for=profile_for,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user

    @staticmethod
    async def login_with_email(
        db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user is None or user.password_hash is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    @staticmethod
    async def create_tokens(user: User) -> TokenResponse:
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id),
        )

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession, refresh_token: str
    ) -> Optional[TokenResponse]:
        payload = verify_token(refresh_token, "refresh")
        if payload is None:
            return None

        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return await AuthService.create_tokens(user)

    @staticmethod
    async def update_last_login(db: AsyncSession, user: User) -> None:
        user.last_login = datetime.now(timezone.utc)
        user.last_active = datetime.now(timezone.utc)
        await db.commit()

    @staticmethod
    async def set_password(db: AsyncSession, user: User, password: str) -> None:
        user.password_hash = get_password_hash(password)
        await db.commit()


auth_service = AuthService()
