import pytest
import httpx
import uuid
from src.main import app
from httpx import AsyncClient

# This test requires real Supabase environment variables in .env
# We intentionally do NOT use mocks here.

@pytest.mark.asyncio
async def test_supabase_health_real():
    """Verify that the health check works."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_real_register_and_login():
    """
    End-to-end test with real Supabase connection.
    1. Register a random user
    2. Login with that user
    """
    random_suffix = str(uuid.uuid4())[:8]
    email = f"test_user_{random_suffix}@example.com"
    password = "SecurePassword123!"
    full_name = "Real Test User"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Register
        reg_payload = {
            "email": email,
            "password": password,
            "full_name": full_name
        }
        print(f"\nRegistering user: {email}")
        reg_response = await ac.post("/api/v1/auth/register", json=reg_payload)
        
        # registration might fail if Supabase is down or rate limited
        assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
        assert "User created" in reg_response.json()["message"]

        # 2. Login
        login_payload = {
            "email": email,
            "password": password
        }
        print(f"Logging in user: {email}")
        login_response = await ac.post("/api/v1/auth/login", json=login_payload)
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        data = login_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == email

        # 3. Verify user
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_response = await ac.get("/api/v1/auth/user", headers=headers)
        
        assert user_response.status_code == 200
        assert user_response.json()["email"] == email

        print(f"Successfully verified real connection for {email}")
