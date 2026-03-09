import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_health_check_returns_200():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "gas-ai-orchestrator"}

@pytest.mark.asyncio
async def test_analyze_without_user_header_returns_401():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "type": "technical",
            "prompt": "Test prompt"
        }
        response = await ac.post("/analyze", json=payload)
    assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_analyze_with_invalid_type_returns_400():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "type": "invalid_type",
            "prompt": "Test prompt"
        }
        headers = {"X-User-ID": "test_user_123"}
        response = await ac.post("/analyze", json=payload, headers=headers)
        
    assert response.status_code == 400
    assert "not found or unsupported" in response.text
