"""
GAS Bot — Feed Worker
Background interval-based worker (NOT queue-based).
Fetches news + calendar every 5 minutes and caches in Redis.
Workers and handlers can read cache:feed:news and cache:feed:calendar.
"""
import asyncio
import httpx

from src.config import settings
from src.services import cache
from src.utils.logger import logger

_INTERVAL = 300  # 5 minutes


class FeedWorker:
    def __init__(self):
        self._running = True

    async def run(self) -> None:
        logger.info("feed_worker_started", interval=_INTERVAL)
        # Fetch once immediately on startup
        await self._fetch_all()
        while self._running:
            await asyncio.sleep(_INTERVAL)
            try:
                await self._fetch_all()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("feed_worker_error", error=str(e))

    def stop(self) -> None:
        self._running = False

    async def _fetch_all(self) -> None:
        async with httpx.AsyncClient(timeout=15) as client:
            await asyncio.gather(
                self._fetch_news(client),
                self._fetch_calendar(client),
                return_exceptions=True,
            )

    async def _fetch_news(self, client: httpx.AsyncClient) -> None:
        # terminal-backend live news
        terminal_url = settings.WEB_BACKEND_URL.replace(":8005", ":8085")
        resp = await client.get(f"{terminal_url}/terminal/news")
        if resp.status_code == 200:
            data = resp.json()
            news = data.get("news") or data.get("items") or []
            if news:
                await cache.set_feed("news", news)
                logger.info("feed_news_cached", count=len(news))

    async def _fetch_calendar(self, client: httpx.AsyncClient) -> None:
        # calendar-news-service via terminal-backend
        terminal_url = settings.WEB_BACKEND_URL.replace(":8005", ":8085")
        resp = await client.get(f"{terminal_url}/terminal/calendar")
        if resp.status_code == 200:
            events = resp.json()
            items  = events.get("events") or events.get("items") or (events if isinstance(events, list) else [])
            if items:
                await cache.set_feed("calendar", items)
                logger.info("feed_calendar_cached", count=len(items))
