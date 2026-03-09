"""
News fetcher for gas-rag-macro.

Uses NewsAPI.org as primary source and Google News RSS as fallback.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timezone

import feedparser
import httpx

from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

# Symbol → search keywords mapping
SYMBOL_KEYWORDS: dict[str, list[str]] = {
    "XAUUSD": ["gold", "XAU", "inflation", "Fed", "FOMC"],
    "EURUSD": ["EUR", "euro", "ECB", "eurozone"],
    "USDJPY": ["JPY", "yen", "Bank of Japan", "BOJ"],
    "GBPUSD": ["GBP", "pound", "Bank of England", "BOE"],
    "BTCUSD": ["bitcoin", "BTC", "crypto", "cryptocurrency"],
    "USOIL": ["oil", "crude", "OPEC", "WTI", "Brent"],
    "US30": ["Dow Jones", "US stocks", "Wall Street", "NYSE"],
    "NAS100": ["NASDAQ", "tech stocks", "SPX", "S&P"],
}


def _get_keywords(symbol: str) -> list[str]:
    """Return search keywords for a symbol."""
    keywords = SYMBOL_KEYWORDS.get(symbol.upper())
    if keywords:
        return keywords
    # Generic fallback: use raw symbol
    return [symbol]


class NewsAPIFetcher:
    """Fetches news from NewsAPI.org."""

    BASE_URL = "https://newsapi.org/v2/everything"

    async def fetch(self, symbol: str, limit: int = 10) -> list[dict]:
        if not settings.NEWS_API_KEY:
            return []

        keywords = " OR ".join(_get_keywords(symbol)[:3])
        params = {
            "q": keywords,
            "sortBy": "publishedAt",
            "pageSize": limit,
            "language": "en",
            "apiKey": settings.NEWS_API_KEY,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            logger.warning("news_api.fetch.error", error=str(exc))
            return []

        articles = []
        for art in data.get("articles", []):
            articles.append({
                "title": art.get("title", ""),
                "source": art.get("source", {}).get("name", "NewsAPI"),
                "time": art.get("publishedAt", ""),
                "url": art.get("url"),
                "sentiment": None,
            })
        return articles


class GoogleNewsRSSFetcher:
    """Fetches news from Google News RSS (free, no API key required)."""

    def _rss_url(self, query: str) -> str:
        import urllib.parse
        q = urllib.parse.quote(query)
        return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"

    async def fetch(self, symbol: str, limit: int = 10) -> list[dict]:
        keywords = _get_keywords(symbol)
        query = " OR ".join(keywords[:2])
        url = self._rss_url(query)

        try:
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, url)
        except Exception as exc:
            logger.warning("google_news.fetch.error", error=str(exc))
            return []

        articles = []
        for entry in feed.entries[:limit]:
            articles.append({
                "title": entry.get("title", ""),
                "source": entry.get("source", {}).get("title", "Google News") if hasattr(entry, "source") else "Google News",
                "time": entry.get("published", ""),
                "url": entry.get("link"),
                "sentiment": None,
            })
        return articles


class NewsFetcher:
    """
    Aggregated news fetcher.
    Tries NewsAPI first; falls back to Google News RSS.
    """

    def __init__(self):
        self._newsapi = NewsAPIFetcher()
        self._google = GoogleNewsRSSFetcher()

    async def fetch(self, symbol: str, limit: int = 10) -> list[dict]:
        """
        Fetch latest news articles for the given symbol.

        Args:
            symbol: Trading symbol (e.g. 'XAUUSD').
            limit: Maximum number of articles to return.

        Returns:
            List of news article dicts.
        """
        articles = await self._newsapi.fetch(symbol, limit)
        if articles:
            logger.info("news_fetcher.newsapi", count=len(articles), symbol=symbol)
            return articles

        articles = await self._google.fetch(symbol, limit)
        logger.info("news_fetcher.google_rss", count=len(articles), symbol=symbol)
        return articles
