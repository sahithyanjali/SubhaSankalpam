from datetime import timedelta

import redis.asyncio as redis

from app.core.config import settings
from app.core.security import generate_otp

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class OTPService:
    OTP_PREFIX = "otp:"
    OTP_ATTEMPTS_PREFIX = "otp_attempts:"
    MAX_ATTEMPTS = 5

    @staticmethod
    async def send_otp(phone: str) -> str:
        otp = generate_otp(settings.OTP_LENGTH)

        # Store OTP in Redis with expiry
        key = f"{OTPService.OTP_PREFIX}{phone}"
        await redis_client.setex(
            key, timedelta(minutes=settings.OTP_EXPIRE_MINUTES), otp
        )

        # Reset attempts
        attempts_key = f"{OTPService.OTP_ATTEMPTS_PREFIX}{phone}"
        await redis_client.delete(attempts_key)

        # In production, send via Twilio
        # For now, return OTP (remove in production)
        if settings.TWILIO_ACCOUNT_SID:
            await OTPService._send_sms(phone, f"Your SubhaSankalpam OTP is: {otp}")

        return otp

    @staticmethod
    async def verify_otp(phone: str, otp: str) -> bool:
        # Check attempts
        attempts_key = f"{OTPService.OTP_ATTEMPTS_PREFIX}{phone}"
        attempts = await redis_client.get(attempts_key)
        if attempts and int(attempts) >= OTPService.MAX_ATTEMPTS:
            return False

        # Get stored OTP
        key = f"{OTPService.OTP_PREFIX}{phone}"
        stored_otp = await redis_client.get(key)

        if stored_otp is None:
            return False

        if stored_otp != otp:
            await redis_client.incr(attempts_key)
            await redis_client.expire(
                attempts_key, timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
            )
            return False

        # OTP verified - cleanup
        await redis_client.delete(key)
        await redis_client.delete(attempts_key)
        return True

    @staticmethod
    async def _send_sms(phone: str, message: str) -> None:
        try:
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone,
            )
        except Exception:
            pass  # Log error in production


otp_service = OTPService()
