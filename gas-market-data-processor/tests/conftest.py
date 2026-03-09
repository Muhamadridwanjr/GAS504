import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_redis():
    """Provides a mocked async Redis client."""
    mock = AsyncMock()
    # By default mock its async methods
    mock.lpush = AsyncMock(return_value=1)
    mock.ltrim = AsyncMock(return_value=True)
    mock.set = AsyncMock(return_value=True)
    mock.get = AsyncMock(return_value=None)
    mock.lrange = AsyncMock(return_value=[])
    mock.keys = AsyncMock(return_value=[])
    return mock
