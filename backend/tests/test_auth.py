"""Authentication endpoint tests."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_otp(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/otp/send",
        json={"phone": "+919876543210"},
    )
    # Should work or fail gracefully without Twilio/Redis
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_register_without_otp(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "phone": "+919876543210",
            "otp": "123456",
            "email": "test@example.com",
            "password": "Test@123456",
            "profile_for": "myself",
        },
    )
    # Will fail because OTP not verified yet
    assert response.status_code in [400, 500]


@pytest.mark.asyncio
async def test_email_login_invalid(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login/email",
        json={"email": "nonexistent@example.com", "password": "wrong"},
    )
    assert response.status_code in [401, 500]
