"""
Pytest fixtures for gas-rag-macro tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

import os
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("DEFAULT_PROVIDER", "openai")


@pytest.fixture
def mock_vector_store():
    vs = AsyncMock()
    vs.initialize = AsyncMock()
    vs.similarity_search = AsyncMock(return_value=[
        {"content": "Gold historically rises when CPI beats expectations.", "metadata": {"source": "test"}}
    ])
    vs.add_documents = AsyncMock(return_value=1)
    return vs


@pytest.fixture
def mock_provider_router():
    router = AsyncMock()
    router.generate = AsyncMock(return_value=(
        '{"summary":"Bearish macro outlook for XAUUSD","sentiment":"bearish","confidence":0.7,'
        '"key_factors":[{"factor":"CPI","impact":"USD strength","probability":0.7}],'
        '"historical_reaction":"Gold dropped 0.5% on CPI beat","sources":["Bloomberg"]}',
        "openai",
        "gpt-4o",
    ))
    return router


@pytest.fixture
def mock_market_client():
    client = AsyncMock()
    client.get_price_data = AsyncMock(return_value={
        "symbol": "XAUUSD",
        "close": 1950.0,
        "high": 1965.0,
        "low": 1940.0,
        "change_pct": -0.5,
    })
    client.close = AsyncMock()
    return client


@pytest.fixture
def app(mock_vector_store, mock_provider_router, mock_market_client):
    from src.main import app as _app
    from src.core.rag_engine import RAGEngine

    engine = RAGEngine(
        vector_store=mock_vector_store,
        market_client=mock_market_client,
        provider_router=mock_provider_router,
    )
    engine.init_cache = AsyncMock()
    engine.news_fetcher = AsyncMock()
    engine.news_fetcher.fetch = AsyncMock(return_value=[])
    engine.calendar_fetcher = AsyncMock()
    engine.calendar_fetcher.fetch = AsyncMock(return_value=[])
    engine._redis = None

    _app.state.rag_engine = engine
    _app.state.vector_store = mock_vector_store
    _app.state.market_client = mock_market_client
    return _app


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c
