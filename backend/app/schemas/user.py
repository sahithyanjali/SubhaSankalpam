from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import ProfileFor, UserRole, UserStatus


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: str
    profile_for: ProfileFor = ProfileFor.MYSELF


class UserCreate(UserBase):
    password: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    device_token: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: Optional[str] = None
    phone: str
    role: UserRole
    status: UserStatus
    profile_for: ProfileFor
    is_verified: bool
    verified_badge: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
