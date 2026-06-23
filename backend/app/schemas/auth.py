from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class OTPRequest(BaseModel):
    phone: str = Field(
        ..., pattern=r"^\+?[1-9]\d{9,14}$", description="Phone number with country code"
    )


class OTPVerify(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{9,14}$")
    otp: str = Field(..., min_length=6, max_length=6)


class EmailLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{9,14}$")
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    profile_for: str = Field(default="myself")


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str
    success: bool = True
