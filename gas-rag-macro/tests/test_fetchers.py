"""
Fetcher tests for gas-rag-macro.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_news_fetcher_falls_back_to_google():
    """When NewsAPI key is missing, fetcher falls back to Google News RSS."""
    from src.fetchers.news import NewsFetcher

    fetcher = NewsFetcher()
    # Mock google fetcher to return fake articles
    fetcher._newsapi.fetch = AsyncMock(return_value=[])
    fetcher._google.fetch = AsyncMock(return_value=[
        {"title": "Gold hits record high", "source": "Google News", "time": "2025-01-01", "url": None, "sentiment": None}
    ])

    articles = await fetcher.fetch("XAUUSD", limit=5)
    assert len(articles) == 1
    assert articles[0]["title"] == "Gold hits record high"


@pytest.mark.asyncio
async def test_news_fetcher_uses_newsapi_when_available():
    from src.fetchers.news import NewsFetcher

    fetcher = NewsFetcher()
    fetcher._newsapi.fetch = AsyncMock(return_value=[
        {"title": "CPI beats expectations", "source": "Bloomberg", "time": "2025-01-01", "url": None, "sentiment": None}
    ])
    fetcher._google.fetch = AsyncMock(return_value=[])

    articles = await fetcher.fetch("XAUUSD", limit=5)
    assert len(articles) == 1
    assert articles[0]["source"] == "Bloomberg"


@pytest.mark.asyncio
async def test_market_client_returns_none_on_connection_error():
    from src.fetchers.market import MarketDataClient

    client = MarketDataClient()
    # Force connection error immediately
    import httpx
    client._client = MagicMock()
    client._client.is_closed = False

    async def raise_connect_error(*a, **kw):
        raise httpx.ConnectError("refused")

    client._client.get = raise_connect_error

    result = await client.get_price_data("XAUUSD")
    assert result is None


@pytest.mark.asyncio
async def test_calendar_fetcher_handles_error():
    from src.fetchers.calendar import CalendarFetcher

    fetcher = CalendarFetcher()
    fetcher._ff.fetch = AsyncMock(return_value=[])

    events = await fetcher.fetch("EURUSD")
    assert events == []
