"""
EcoCal worker — fetches economic calendar from FXStreet via ecocal library.

Filter policy (saves bandwidth + DB space):
  - Countries / currencies : USD EUR JPY GBP CNY CHF AUD CAD NZD
  - Impact                 : high, medium  (low is discarded)
"""
from datetime import datetime
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import EconomicEvent
from src.lib.logger import get_logger

logger = get_logger(__name__)

# ── Filters applied before DB insert ─────────────────────────────────────────
_PRIORITY_CURRENCIES = {"USD", "EUR", "JPY", "GBP", "CNY", "CHF", "AUD", "CAD", "NZD"}
_PRIORITY_IMPACTS    = {"high", "medium"}


def _parse_importance(raw) -> str:
    """Normalise impact to lowercase string."""
    return str(raw or "low").strip().lower()


def _parse_time(time_val) -> datetime:
    """Parse ecocal datetime value to a Python datetime."""
    if pd.isnull(time_val):
        return datetime.utcnow()
    if isinstance(time_val, str):
        try:
            if "/" in time_val:
                return datetime.strptime(time_val, "%m/%d/%Y %H:%M:%S")
            return datetime.fromisoformat(time_val.replace("Z", "+00:00"))
        except Exception:
            return datetime.utcnow()
    if isinstance(time_val, datetime):
        return time_val
    return datetime.utcnow()


def _safe_float(val) -> float | None:
    """Convert to float, return None if not parseable."""
    try:
        s = str(val).replace(",", "")
        if s.replace(".", "", 1).lstrip("-").isdigit():
            return float(s)
    except Exception:
        pass
    return None


async def fetch_calendar_events(db: AsyncSession, start_date=None, end_date=None):
    """
    Fetch and persist calendar events from FXStreet via ecocal.

    Only HIGH and MEDIUM impact events for major economies are saved.
    LOW impact events are silently discarded.
    """
    try:
        from ecocal import Calendar
        logger.info(
            "[ecocal] Fetching calendar %s → %s (filter: %s | high/medium only)",
            start_date, end_date, ", ".join(sorted(_PRIORITY_CURRENCIES)),
        )

        # Default to today → +7 days if no range given
        if not start_date:
            from datetime import date, timedelta
            start_date = date.today().strftime("%Y-%m-%d")
        if not end_date:
            from datetime import date, timedelta
            end_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

        ec = Calendar(
            startHorizon=start_date,
            endHorizon=end_date,
            withDetails=False,     # False = fast (no per-event detail scrape)
            withProgressBar=False,
            nbThreads=20,
            preBuildCalendar=True,
        )

        # Prefer detailedCalendar, fall back to calendar
        df = None
        if hasattr(ec, "detailedCalendar") and ec.detailedCalendar is not None and len(ec.detailedCalendar) > 0:
            df = ec.detailedCalendar
            logger.info("[ecocal] Using detailedCalendar — %d raw rows", len(df))
        elif hasattr(ec, "calendar") and ec.calendar is not None and len(ec.calendar) > 0:
            df = ec.calendar
            logger.info("[ecocal] Using basic calendar — %d raw rows", len(df))

        if df is None or len(df) == 0:
            logger.warning("[ecocal] No data returned from ecocal.")
            return []

        count_raw    = len(df)
        count_saved  = 0
        count_skip_ccy    = 0
        count_skip_impact = 0

        for _, row in df.iterrows():
            try:
                title      = str(row.get("Name") or row.get("name") or row.get("Title") or "Unknown")
                country    = str(row.get("Currency") or row.get("countryCode") or "GLOBAL").upper().strip()
                importance = _parse_importance(row.get("Impact") or row.get("Importance"))

                # ── Filter 1: major economies only ─────────────────────────
                if country not in _PRIORITY_CURRENCIES:
                    count_skip_ccy += 1
                    continue

                # ── Filter 2: HIGH / MEDIUM impact only ────────────────────
                if importance not in _PRIORITY_IMPACTS:
                    count_skip_impact += 1
                    continue

                time_val = _parse_time(
                    row.get("dateUtc") or row.get("Date") or row.get("Start")
                )

                event = EconomicEvent(
                    provider       = "ecocal",
                    title          = title,
                    country        = country,
                    importance     = importance,
                    time_utc       = time_val,
                    actual_value   = _safe_float(row.get("actual")),
                    forecast_value = _safe_float(row.get("consensus")),
                    previous_value = _safe_float(row.get("previous")),
                    unit           = str(row.get("unit") or ""),
                )
                db.add(event)
                count_saved += 1

            except Exception as ex:
                logger.debug("[ecocal] Row mapping error: %s", ex)

        await db.commit()
        logger.info(
            "[ecocal] Done — %d raw rows | %d saved | %d skipped (minor ccy) | %d skipped (low impact)",
            count_raw, count_saved, count_skip_ccy, count_skip_impact,
        )
        return [{"title": "Ingested", "count": count_saved}]

    except Exception as e:
        logger.error("[ecocal] Critical error: %s", e)
        return []
