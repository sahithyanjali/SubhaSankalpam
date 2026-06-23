from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    EmailLogin,
    MessageResponse,
    OTPRequest,
    OTPVerify,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth.auth_service import auth_service
from app.services.auth.otp_service import otp_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/otp/send", response_model=MessageResponse)
async def send_otp(request: OTPRequest):
    """Send OTP to mobile number for login/registration."""
    await otp_service.send_otp(request.phone)
    # In production, don't return OTP
    return MessageResponse(message=f"OTP sent successfully to {request.phone}", success=True)


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(request: OTPVerify, db: AsyncSession = Depends(get_db)):
    """Verify OTP and return JWT tokens."""
    is_valid = await otp_service.verify_otp(request.phone, request.otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP",
        )

    user = await auth_service.get_or_create_user_by_phone(db, request.phone)
    await auth_service.update_last_login(db, user)
    return await auth_service.create_tokens(user)


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user after OTP verification."""
    user = await auth_service.get_or_create_user_by_phone(db, request.phone, request.profile_for)

    if request.email:
        user.email = request.email
    if request.password:
        await auth_service.set_password(db, user, request.password)

    await db.commit()
    return await auth_service.create_tokens(user)


@router.post("/login/email", response_model=TokenResponse)
async def login_email(request: EmailLogin, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    user = await auth_service.login_with_email(db, request.email, request.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    await auth_service.update_last_login(db, user)
    return await auth_service.create_tokens(user)


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    tokens = await auth_service.refresh_access_token(db, request.refresh_token)
    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return tokens
