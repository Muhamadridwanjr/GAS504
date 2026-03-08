"""Scheduler for periodic calendar ingestion — auto-ingest yesterday to next 7 days."""
import asyncio
from datetime import datetime, timedelta
from src.lib.logger import get_logger
from src.db.database import async_session

logger = get_logger(__name__)


def _date_str(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


async def run_calendar_ingestion():
    """Ingest ecocal events: yesterday → next 7 days. Called on startup and periodically."""
    from src.ingestion.ecocal_worker import fetch_calendar_events

    now = datetime.utcnow()
    start = now - timedelta(days=1)
    end   = now + timedelta(days=7)

    start_str = _date_str(start)
    end_str   = _date_str(end)

    logger.info("🗓 Scheduler: ingesting %s → %s", start_str, end_str)

    try:
        async with async_session() as db:
            result = await fetch_calendar_events(db, start_date=start_str, end_date=end_str)
            logger.info("✅ Scheduler ingestion done: %s events saved", len(result))
    except Exception as e:
        logger.error("❌ Scheduler ingestion error: %s", e)


async def start_scheduler(interval_hours: int = 6):
    """Run ingestion once on startup, then every interval_hours hours."""
    await run_calendar_ingestion()

    while True:
        await asyncio.sleep(interval_hours * 3600)
        await run_calendar_ingestion()
