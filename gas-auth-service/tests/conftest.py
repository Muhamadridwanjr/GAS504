import pytest
import asyncio
from httpx import AsyncClient
from src.main import app
from unittest.mock import AsyncMock, patch

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_supabase():
    with patch("src.core.supabase_client.supabase") as mock:
        yield mock

@pytest.fixture
def mock_user_service():
    with patch("src.services.user_service_client.user_service_client") as mock:
        mock.create_profile = AsyncMock()
        yield mock
