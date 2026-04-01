"""
Scheduler for economic calendar ingestion (ecocal / FXStreet).

Ingestion   : 05:05 WIB daily (5-min offset after fundamental service).
News Trigger: every 15 min during 05:00–22:00 WIB.
Filter      : HIGH + MEDIUM impact only, major economies only.
After run   : service sleeps; news trigger stays active for real-time alerts.

Priority currencies : USD EUR JPY GBP CNY CHF AUD CAD NZD
Priority impacts    : high  medium   (LOW ignored)

Redis keys written:
  calendar:analysis       – AI sentiment per currency (TTL 25h)
  news:upcoming_triggers  – events within next 60 min (TTL 1h)

Redis pub/sub channel:
  news:triggers           – real-time event alert (subscribed by signal engine)
"""
import asyncio
import json
from datetime import datetime, timedelta, timezone
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.lib.logger import get_logger
from src.db.database import async_session

logger = get_logger(__name__)
WIB = pytz.timezone("Asia/Jakarta")

# ─── Filters ─────────────────────────────────────────────────────────────────
PRIORITY_CURRENCIES = {"USD", "EUR", "JPY", "GBP", "CNY", "CHF", "AUD", "CAD", "NZD"}
PRIORITY_IMPACTS    = {"high", "medium"}        # ecocal uses lowercase
TRIGGER_WINDOW_MIN  = 60                        # alert this many minutes before event

# Currency → affected markets
_CURRENCY_MARKETS = {
    "USD": ["FOREX", "CRYPTO", "COMMODITIES", "INDICES"],
    "EUR": ["FOREX", "INDICES"],
    "JPY": ["FOREX", "INDICES"],
    "GBP": ["FOREX", "INDICES"],
    "CNY": ["FOREX", "COMMODITIES"],
    "CHF": ["FOREX"],
    "AUD": ["FOREX", "COMMODITIES"],
    "CAD": ["FOREX", "COMMODITIES"],
    "NZD": ["FOREX"],
}

# Keyword → bias logic
_MACRO_SIGNALS = {
    "cpi":           {"bias": "hawkish_if_beat", "markets": ["FOREX", "GOLD", "BONDS"]},
    "inflation":     {"bias": "hawkish_if_beat", "markets": ["FOREX", "GOLD"]},
    "interest rate": {"bias": "bullish_ccy_if_hike", "markets": ["FOREX", "BONDS"]},
    "gdp":           {"bias": "bullish_if_beat",  "markets": ["FOREX", "INDICES"]},
    "nfp":           {"bias": "bullish_if_beat",  "markets": ["FOREX", "GOLD", "INDICES"]},
    "non-farm":      {"bias": "bullish_if_beat",  "markets": ["FOREX", "GOLD"]},
    "unemployment":  {"bias": "bearish_if_beat",  "markets": ["FOREX", "INDICES"]},
    "pmi":           {"bias": "bullish_if_above50","markets": ["FOREX", "INDICES", "COMMODITIES"]},
    "retail sales":  {"bias": "bullish_if_beat",  "markets": ["FOREX"]},
    "trade balance": {"bias": "mixed",            "markets": ["FOREX"]},
    "fomc":          {"bias": "high_volatility",  "markets": ["ALL"]},
    "ecb":           {"bias": "high_volatility",  "markets": ["FOREX"]},
    "boj":           {"bias": "high_volatility",  "markets": ["FOREX"]},
    "boe":           {"bias": "high_volatility",  "markets": ["FOREX"]},
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _classify_event(
    title: str,
    actual: float | None,
    forecast: float | None,
    country: str,
) -> dict:
    """Quick AI classification of a single calendar event."""
    title_lower = title.lower()
    affected    = list(_CURRENCY_MARKETS.get(country, ["FOREX"]))
    signal_type = "general"
    market_bias = "NEUTRAL"

    for keyword, info in _MACRO_SIGNALS.items():
        if keyword not in title_lower:
            continue
        signal_type = keyword
        extra = info["markets"]
        if "ALL" in extra:
            extra = ["FOREX", "CRYPTO", "COMMODITIES", "INDICES", "BONDS"]
        affected = list(set(affected + extra))

        if actual is not None and forecast is not None:
            beat = actual > forecast
            b    = info["bias"]
            if   b == "hawkish_if_beat"    and beat:  market_bias = "HAWKISH"
            elif b == "bullish_if_beat"    and beat:  market_bias = "BULLISH"
            elif b == "bullish_ccy_if_hike"and beat:  market_bias = "BULLISH"
            elif b == "bearish_if_beat"    and beat:  market_bias = "BEARISH"
            elif b == "bullish_if_above50":            market_bias = "BULLISH" if (actual or 0) >= 50 else "BEARISH"
            elif b == "high_volatility":               market_bias = "HIGH_VOLATILITY"
        break

    return {"signal_type": signal_type, "market_bias": market_bias, "affected_markets": affected}


# ─── AI Calendar Analysis ────────────────────────────────────────────────────

async def _run_calendar_ai_analysis():
    """
    Classify today's HIGH/MEDIUM events, score sentiment per currency,
    and write result to Redis `calendar:analysis`.
    """
    from src.cache.redis_cache import RedisCache
    from sqlalchemy import text

    logger.info("[2/3] Running AI calendar analysis...")
    try:
        today_utc    = datetime.utcnow().date()
        tomorrow_utc = (datetime.utcnow() + timedelta(days=1)).date()

        async with async_session() as db:
            result = await db.execute(
                text("""
                    SELECT title, country, importance, time_utc,
                           actual_value, forecast_value, previous_value
                    FROM economic_events
                    WHERE DATE(time_utc) BETWEEN :today AND :tomorrow
                      AND importance IN ('high', 'medium')
                      AND country    IN ('USD','EUR','JPY','GBP','CNY','CHF','AUD','CAD','NZD')
                    ORDER BY time_utc ASC
                    LIMIT 60
                """),
                {"today": today_utc, "tomorrow": tomorrow_utc},
            )
            rows = result.fetchall()

        if not rows:
            logger.info("[2/3] No priority events today — skipping analysis.")
            return

        events_out   = []
        ccy_biases: dict[str, list] = {}

        for row in rows:
            clf = _classify_event(row.title, row.actual_value, row.forecast_value, row.country)
            events_out.append({
                "title":            row.title,
                "country":          row.country,
                "importance":       row.importance,
                "time_utc":         row.time_utc.isoformat() if row.time_utc else None,
                "actual":           row.actual_value,
                "forecast":         row.forecast_value,
                "previous":         row.previous_value,
                "signal_type":      clf["signal_type"],
                "market_bias":      clf["market_bias"],
                "affected_markets": clf["affected_markets"],
            })
            ccy_biases.setdefault(row.country, []).append(clf["market_bias"])

        # Aggregate per currency
        currency_sentiment: dict = {}
        for ccy, biases in ccy_biases.items():
            bull     = sum(1 for b in biases if "BULLISH" in b or "HAWKISH" in b)
            bear     = sum(1 for b in biases if "BEARISH" in b)
            volatile = sum(1 for b in biases if "VOLATILITY" in b)
            total    = len(biases)
            score    = int((bull / total) * 100) if total else 50
            currency_sentiment[ccy] = {
                "score":            score,
                "bias":             "BULLISH" if score >= 60 else ("BEARISH" if score <= 40 else "NEUTRAL"),
                "events":           total,
                "high_volatility":  volatile > 0,
            }

        analysis = {
            "generated_at":           datetime.now(WIB).isoformat(),
            "total_events":           len(events_out),
            "priority_events":        events_out,
            "currency_sentiment":     currency_sentiment,
            "risk_on_currencies":     [c for c, v in currency_sentiment.items() if v["bias"] == "BULLISH"],
            "risk_off_currencies":    [c for c, v in currency_sentiment.items() if v["bias"] == "BEARISH"],
            "high_volatility_expected": any(v["high_volatility"] for v in currency_sentiment.values()),
        }

        cache = RedisCache()
        await cache.connect()
        await cache.set("calendar:analysis", json.dumps(analysis, default=str), ttl=90000)
        await cache.close()

        logger.info(
            "[2/3] Calendar AI analysis complete — %d events, %d currencies scored.",
            len(events_out), len(currency_sentiment),
        )
    except Exception as e:
        logger.error("[2/3] Calendar AI analysis error: %s", e)


# ─── News Trigger Engine ─────────────────────────────────────────────────────

async def _news_trigger_engine():
    """
    Runs every 15 min during 05:00–22:00 WIB.
    Checks for HIGH/MEDIUM events from major currencies within the next 60 min.
    Publishes to Redis key `news:upcoming_triggers` and channel `news:triggers`.
    Signal engine and realtime-hub can subscribe to this channel.
    """
    from src.cache.redis_cache import RedisCache
    from sqlalchemy import text

    now_utc    = datetime.utcnow().replace(tzinfo=timezone.utc)
    window_end = now_utc + timedelta(minutes=TRIGGER_WINDOW_MIN)

    try:
        async with async_session() as db:
            result = await db.execute(
                text("""
                    SELECT title, country, importance, time_utc,
                           forecast_value, previous_value
                    FROM economic_events
                    WHERE time_utc BETWEEN :now AND :end
                      AND importance IN ('high', 'medium')
                      AND country    IN ('USD','EUR','JPY','GBP','CNY','CHF','AUD','CAD','NZD')
                    ORDER BY time_utc ASC
                    LIMIT 20
                """),
                {"now": now_utc.replace(tzinfo=None), "end": window_end.replace(tzinfo=None)},
            )
            rows = result.fetchall()

        if not rows:
            return

        triggers = []
        for row in rows:
            t_utc = row.time_utc
            if t_utc.tzinfo is None:
                t_utc = t_utc.replace(tzinfo=timezone.utc)
            mins_away = int((t_utc - now_utc).total_seconds() / 60)
            time_wib  = t_utc.astimezone(WIB).strftime("%H:%M WIB")
            clf       = _classify_event(row.title, None, row.forecast_value, row.country)
            triggers.append({
                "title":            row.title,
                "country":          row.country,
                "importance":       row.importance.upper(),
                "time_utc":         t_utc.isoformat(),
                "time_wib":         time_wib,
                "minutes_away":     mins_away,
                "affected_markets": clf["affected_markets"],
                "signal_type":      clf["signal_type"],
            })

        payload = {
            "triggered_at": now_utc.isoformat(),
            "count":        len(triggers),
            "events":       triggers,
        }
        payload_str = json.dumps(payload, default=str)

        cache = RedisCache()
        await cache.connect()
        # Store latest trigger snapshot (TTL 1h)
        await cache.set("news:upcoming_triggers", payload_str, ttl=3600)
        # Publish to real-time channel
        if cache._redis:
            await cache._redis.publish("news:triggers", payload_str)
        await cache.close()

        logger.info(
            "[NEWS TRIGGER] %d event(s) within %d min: %s",
            len(triggers),
            TRIGGER_WINDOW_MIN,
            " | ".join(f"{t['country']} {t['title'][:28]}@{t['time_wib']}" for t in triggers),
        )
    except Exception as e:
        logger.error("[NEWS TRIGGER] Error: %s", e)


# ─── Main Ingestion Pipeline ─────────────────────────────────────────────────

async def run_calendar_ingestion():
    """
    Full calendar ingestion pipeline — runs at 05:05 WIB.

    1. Fetch FXStreet calendar via ecocal (yesterday → +7 days)
    2. Filter: major currencies + HIGH/MEDIUM impact only
    3. Store to DB
    4. Run AI analysis → write calendar:analysis to Redis
    5. Log sleep window
    """
    from src.ingestion.ecocal_worker import fetch_calendar_events

    now_utc   = datetime.utcnow()
    start_str = (now_utc - timedelta(days=1)).strftime("%Y-%m-%d")
    end_str   = (now_utc + timedelta(days=7)).strftime("%Y-%m-%d")

    now_wib = datetime.now(WIB).strftime("%H:%M WIB")
    logger.info(
        "=== [PIPELINE START] Calendar Ingestion (%s): %s → %s ===",
        now_wib, start_str, end_str,
    )

    try:
        # ── 1: Fetch + filter + store ──────────────────────────────────────
        logger.info("[1/3] Fetching FXStreet calendar via ecocal...")
        async with async_session() as db:
            result = await fetch_calendar_events(db, start_date=start_str, end_date=end_str)
        count = result[0]["count"] if result else 0
        logger.info(
            "[1/3] Fetched %d events (major currencies + HIGH/MEDIUM only).", count,
        )

        # ── 2: AI Analysis ─────────────────────────────────────────────────
        await _run_calendar_ai_analysis()

        # ── 3: Done ────────────────────────────────────────────────────────
        next_run = (
            datetime.now(WIB)
            .replace(hour=5, minute=5, second=0, microsecond=0)
            + timedelta(days=1)
        )
        logger.info(
            "=== [PIPELINE COMPLETE] %d events stored. AI analysis done. "
            "Next ingest: %s WIB. News trigger remains active 05:00-22:00 WIB. ===",
            count, next_run.strftime("%Y-%m-%d %H:%M"),
        )

    except Exception as e:
        logger.error("[PIPELINE ERROR] Calendar ingestion: %s", e)


# ─── Startup Check ────────────────────────────────────────────────────────────

async def _check_and_run_on_startup():
    """Skip ingest if DB already has today's priority events, else run once."""
    from sqlalchemy import text

    try:
        async with async_session() as db:
            today_utc = datetime.utcnow().date()
            result    = await db.execute(
                text("""
                    SELECT COUNT(*) FROM economic_events
                    WHERE DATE(time_utc) >= :today
                      AND importance IN ('high', 'medium')
                      AND country    IN ('USD','EUR','JPY','GBP','CNY','CHF','AUD','CAD','NZD')
                """),
                {"today": today_utc},
            )
            count = result.scalar()
            if count and count > 0:
                logger.info(
                    "Startup: DB has %d priority events from %s — skipping ingest. "
                    "Running AI analysis on existing data...",
                    count, today_utc,
                )
                await _run_calendar_ai_analysis()
                return
    except Exception as e:
        logger.warning("Startup check failed (%s) — will ingest anyway", e)

    logger.info("Startup: no priority events in DB — running initial ingest...")
    await run_calendar_ingestion()


# ─── Scheduler Lifecycle ─────────────────────────────────────────────────────

async def start_scheduler(interval_hours: int = 6):
    """
    Start APScheduler with two jobs:
      - 05:05 WIB daily  → full calendar ingestion pipeline
      - every 15 min (05:00–22:00 WIB) → news trigger engine
    """
    scheduler = AsyncIOScheduler(timezone=WIB)

    # Daily ingestion at 05:05 WIB
    scheduler.add_job(
        run_calendar_ingestion,
        CronTrigger(hour=5, minute=5, timezone=WIB),
        id="calendar_ingest_daily",
        name="Calendar Ingest (05:05 WIB)",
        replace_existing=True,
        misfire_grace_time=1800,
    )

    # News trigger engine — every 15 min during active hours
    scheduler.add_job(
        _news_trigger_engine,
        CronTrigger(minute="*/15", hour="5-22", timezone=WIB),
        id="news_trigger_engine",
        name="News Trigger Engine (every 15min, 05:00-22:00 WIB)",
        replace_existing=True,
        misfire_grace_time=300,
    )

    scheduler.start()
    await _check_and_run_on_startup()

    now_wib = datetime.now(WIB).strftime("%H:%M WIB")
    logger.info(
        "Calendar scheduler started — ingest 05:05 WIB daily, "
        "news trigger every 15min 05:00-22:00 WIB (current: %s)",
        now_wib,
    )

    # Keep async task alive (APScheduler runs in background thread)
    while True:
        await asyncio.sleep(3600)
