"""Worker using ecocal library to fetch events."""
from src.lib.logger import get_logger
logger = get_logger(__name__)

async def fetch_calendar_events(start_date=None, end_date=None):
    """Fetch events using ecocal. Falls back gracefully if not installed."""
    try:
        from ecocal import Calendar
        ec = Calendar(startHorizon=start_date, endHorizon=end_date, withDetails=True, nbThreads=20, preBuildCalendar=True)
        logger.info("Fetched %d events via ecocal", len(ec.events) if hasattr(ec, "events") else 0)
        return getattr(ec, "events", [])
    except ImportError:
        logger.warning("ecocal not installed — skipping")
        return []
    except Exception as e:
        logger.error("ecocal error: %s", e)
        return []
