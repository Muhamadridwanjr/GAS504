import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint returns 200."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["service"] == "gas-journal-service"

@pytest.mark.asyncio
async def test_trades_requires_user_id():
    """Test that /trades endpoint requires X-User-ID header."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/trades")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_internal_requires_api_key():
    """Test that /internal endpoints require X-API-Key header."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/internal/trades", json={})
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_stats_requires_user_id():
    """Test that /stats endpoint requires X-User-ID header."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/stats")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_analysis_requires_user_id():
    """Test that /analysis endpoint requires X-User-ID header."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/analysis")
        assert response.status_code == 401
