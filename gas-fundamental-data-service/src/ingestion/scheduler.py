"""Scheduler for periodic tedata ingestion from Trading Economics."""
from __future__ import annotations
import asyncio
import json
from concurrent.futures import ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.lib.logger import get_logger

logger = get_logger(__name__)
_scheduler: AsyncIOScheduler | None = None


async def _run_scrape_job():
    """Run tedata scraping in a separate process (Selenium is blocking)."""
    from src.ingestion.te_scraper import scrape_all_sync
    from src.cache.redis_cache import RedisCache

    logger.info("Starting Trading Economics scrape cycle")
    loop = asyncio.get_event_loop()
    try:
        with ProcessPoolExecutor(max_workers=1) as executor:
            results = await loop.run_in_executor(executor, scrape_all_sync, None)

        if not results:
            logger.warning("No results from TE scrape")
            return

        # Cache macro dashboard in Redis (TTL 6 hours)
        cache = RedisCache()
        await cache.connect()
        import datetime
        payload = {
            "last_updated": datetime.datetime.utcnow().isoformat(),
            "indicators": results,
        }
        await cache.set("macro:dashboard", json.dumps(payload), ttl=21600)
        await cache.close()
        logger.info("Scrape complete — cached %d indicators", len(results))

    except Exception as e:
        logger.error("Scrape job failed: %s", e)


def start_scheduler():
    global _scheduler
    _scheduler = AsyncIOScheduler()
    # Run once at startup (after 60s), then every 6 hours
    _scheduler.add_job(_run_scrape_job, "interval", hours=6, id="te_scrape",
                       next_run_time=__import__("datetime").datetime.now() +
                       __import__("datetime").timedelta(seconds=90))
    _scheduler.start()
    logger.info("Scheduler started — TE scrape every 6 hours")


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)


async def run_ingestion_cycle():
    """Manual trigger for a single scrape cycle."""
    await _run_scrape_job()
