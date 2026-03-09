import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from src.main import app


@pytest.mark.asyncio
async def test_follow_requires_user_id():
    """Follow endpoint should return 401 if X-User-ID header is missing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/follow/some-user-id")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_followers_requires_user_id():
    """Followers endpoint should return 401 if X-User-ID header is missing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/follow/followers/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_feed_requires_user_id():
    """Feed endpoint should return 401 if X-User-ID header is missing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/feed")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_internal_ping_requires_api_key():
    """Internal endpoint should return 403 without API key."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/internal/ping")
    assert response.status_code == 403
