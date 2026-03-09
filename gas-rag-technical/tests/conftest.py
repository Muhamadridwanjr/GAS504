"""Pytest configuration and shared fixtures."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_vector_store():
    store = AsyncMock()
    store.query.return_value = []
    store.add_documents.return_value = None
    store.get_stats.return_value = {"type": "chroma", "count": 10, "status": "ok"}
    return store


@pytest.fixture
def mock_market_client():
    client = AsyncMock()
    client.get_market_context.return_value = {
        "symbol": "XAUUSD",
        "timeframe": "H4",
        "ohlc": {"open": 2000, "high": 2010, "low": 1995, "close": 2005},
        "current": {"bid": 2004.5, "ask": 2005.0},
    }
    return client


@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.provider_name = "openai"
    provider.model_name = "gpt-4o"
    provider.generate.return_value = '{"summary":"Test","key_levels":{"support":[1990],"resistance":[2010]},"signal":"BUY","confidence":0.75,"entry":{"price":2005,"stop_loss":1990,"take_profit":[2015]},"reasoning":"Test reasoning","short_term_bias":"bullish","key_risks":[]}'
    return provider


@pytest.fixture
def mock_provider_router(mock_provider):
    router = MagicMock()
    router.get_provider.return_value = mock_provider
    router.get_embedding_provider.return_value = mock_provider
    return router
