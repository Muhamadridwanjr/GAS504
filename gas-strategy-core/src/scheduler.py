
"""
GAS Strategy Core — Automated Data Scheduler
All times in Asia/Jakarta (WIB = UTC+7).

Schedule:
  05:00  → Calendar fetch (ecocal) + news event monitor start
  07:00  → Morning briefing full (VIP Multi-TF + Macro + COT + F/G)
  07:00  → Fundamental/macro data fetch (tedata/TradingEconomics)
  12:00  → Midday refresh (calendar + sentiment update)
  Mon 07:00 → Weekly briefing

MT5 snapshot: skipped on Saturday & Sunday (Exness market closed).
Service sleep: only active jobs run — no constant polling.
"""
import asyncio
import logging
from datetime import date, datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

log = logging.getLogger("gas.scheduler")
WIB = pytz.timezone("Asia/Jakarta")

# ── Pairs to snapshot every morning ───────────────────────────────────────────
MORNING_PAIRS = [
    # Forex Major 10 (Exness)
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
    "AUDUSD", "NZDUSD", "USDCAD", "EURGBP",
    "EURJPY", "GBPJPY",
    # Commodities
    "XAUUSD", "XAGUSD", "USOIL", "UKOIL",
    # Indices (Exness)
    "US30", "US500", "USTEC", "UK100", "GER40",
]

VIP_PAIRS = ["XAUUSD", "BTC/USDT", "BTCUSDT"]
VIP_TIMEFRAMES = ["M5", "M15", "H1", "H4"]
DXY_TIMEFRAMES = ["H1", "H4"]

def candles_to_csv(candles: list) -> str:
    """Format candles list to a compact CSV string for AI."""
    if not candles: return ""
    # newest 10 candles are usually enough for visual context in text
    header = "time,open,high,low,close,vol"
    lines = [header]
    for c in candles[-20:]:  # Take last 20 for context
        t = datetime.fromtimestamp(c['time']).strftime('%H:%M')
        lines.append(f"{t},{c['open']},{c['high']},{c['low']},{c['close']},{c.get('volume',0)}")
    return "\n".join(lines)


def _is_market_weekend() -> bool:
    """
    Returns True if current WIB day is Saturday or Sunday.
    Exness MT5 markets are closed Sat-Sun → skip MT5 data fetch.
    """
    now = datetime.now(WIB)
    return now.weekday() in (5, 6)   # 5=Sat, 6=Sun


# ── Job: Fetch Sentiment (COT + Fear/Greed) ────────────────────────────────────

async def job_fetch_sentiment() -> dict:
    """Fetch COT + Fear/Greed → cache."""
    from src.data.external import fetch_fear_greed, fetch_cot_gold, fetch_cot_dxy
    from src.cache import set_cached_sentiment

    log.info("Scheduler: fetching sentiment data...")
    fear_greed, cot_gold, cot_dxy = await asyncio.gather(
        fetch_fear_greed(),
        fetch_cot_gold(),
        fetch_cot_dxy(),
        return_exceptions=True,
    )

    data = {
        "fear_greed": fear_greed if not isinstance(fear_greed, Exception) else {"error": str(fear_greed)},
        "cot_gold":   cot_gold   if not isinstance(cot_gold,   Exception) else {"error": str(cot_gold)},
        "cot_dxy":    cot_dxy    if not isinstance(cot_dxy,    Exception) else {"error": str(cot_dxy)},
        "fetched_at": datetime.now(WIB).isoformat(),
    }
    await set_cached_sentiment(data)
    log.info("Scheduler: sentiment cached ✓")
    return data


# ── Job: Fetch Fundamental / Macro — 07:00 WIB ────────────────────────────────

async def job_fetch_fundamental() -> dict:
    """
    Fetch macro data from TradingEconomics (tedata scraper).
    Runs once daily at 07:00 WIB. Skips if data unchanged.
    Service goes idle after completion.
    """
    from src.data.macro import get_macro_data
    from src.cache import set_cached_fundamental, get_cached_fundamental

    log.info(f"Scheduler: FUNDAMENTAL fetch started — {datetime.now(WIB).strftime('%H:%M WIB')}")

    # Skip if already fetched today and data is fresh
    existing = await get_cached_fundamental()
    if existing:
        fetched_at = existing.get("fetched_at", "")
        if fetched_at.startswith(date.today().isoformat()):
            log.info("Scheduler: Fundamental already fetched today — skipping (using cache)")
            return existing

    try:
        macro = await asyncio.to_thread(get_macro_data, "United States")
        log.info(f"Scheduler: Macro data fetched — {len(macro) if isinstance(macro, (dict, list)) else 'ok'} entries")
    except Exception as e:
        log.error(f"Scheduler: Macro fetch failed — {e}")
        macro = {"error": str(e)}

    data = {
        "macro": macro,
        "fetched_at": datetime.now(WIB).isoformat(),
        "source": "tradingeconomics-tedata",
    }
    await set_cached_fundamental(data)
    log.info("Scheduler: Fundamental/macro cached ✓  (service now idle until next schedule)")
    return data


# ── Job: Fetch Economic Calendar — 05:00 WIB ──────────────────────────────────

async def job_fetch_calendar() -> list:
    """
    Fetch economic calendar from EcoCal scraper.
    Runs at 05:00 WIB (before market opens). After fetch, starts
    news event monitor that watches for scheduled events and breaking news.
    """
    from src.data.calendar import get_upcoming_events
    from src.cache import set_cached_calendar

    log.info(f"Scheduler: CALENDAR fetch started — {datetime.now(WIB).strftime('%H:%M WIB')}")
    try:
        events = await asyncio.to_thread(
            get_upcoming_events,
            ["USD", "EUR", "GBP", "JPY", "AUD", "CAD"],
            "high",
        )
        log.info(f"Scheduler: Calendar fetched — {len(events)} events")
    except Exception as e:
        log.error(f"Scheduler: Calendar fetch failed — {e}")
        events = [{"error": str(e)}]

    await set_cached_calendar(events)
    log.info("Scheduler: Calendar cached ✓")

    # Start news event monitor after calendar is loaded
    asyncio.create_task(_run_news_event_monitor(events))

    return events


# ── News Event Monitor & Breaking News Trigger ────────────────────────────────

async def _run_news_event_monitor(events: list):
    """
    After calendar fetch, monitor scheduled event times and update sentiment cache.
    Runs until end of trading day (22:00 WIB).
    Calendar is fetched ONCE at 05:00 WIB — no continuous ecocal scraping.
    Service sleeps between checks to minimise server load.
    """
    log.info(f"NewsMonitor: started — watching {len(events)} events (no continuous scraping)")
    triggered_events: set = set()
    check_interval_seconds = 60   # check every 60 seconds

    end_of_day = datetime.now(WIB).replace(hour=22, minute=0, second=0, microsecond=0)

    while datetime.now(WIB) < end_of_day:
        now = datetime.now(WIB)

        # ── Scheduled event trigger ───────────────────────────────────────────
        for ev in events:
            ev_id = str(ev.get("event", "")) + str(ev.get("time", ""))
            if ev_id in triggered_events:
                continue

            ev_time_str = ev.get("time", "")
            if not ev_time_str:
                continue

            try:
                # Parse event time (e.g. "14:30", "08:30 EST" etc.)
                ev_hour, ev_min = int(ev_time_str[:2]), int(ev_time_str[3:5])
                ev_dt = now.replace(hour=ev_hour, minute=ev_min, second=0, microsecond=0)
                # Trigger within 2-minute window of event time
                diff = abs((now - ev_dt).total_seconds())
                if diff <= 120:
                    log.info(f"NewsMonitor: EVENT TRIGGER — {ev.get('event')} @ {ev_time_str}")
                    triggered_events.add(ev_id)
                    asyncio.create_task(_on_scheduled_event(ev))
            except Exception:
                pass

        await asyncio.sleep(check_interval_seconds)

    log.info("NewsMonitor: end of trading day — monitor stopped (service idle until 05:00 WIB)")


async def _on_scheduled_event(event: dict):
    """
    Called when a scheduled economic event time is reached.
    Updates sentiment cache to flag high-impact news active.
    """
    from src.cache import get_cached_sentiment, set_cached_sentiment

    log.info(f"NewsMonitor: processing event — {event.get('event')} | Impact: {event.get('impact')}")
    try:
        sentiment = await get_cached_sentiment() or {}
        sentiment["active_event"] = {
            "event":    event.get("event"),
            "currency": event.get("currency"),
            "impact":   event.get("impact"),
            "time_wib": datetime.now(WIB).strftime("%H:%M WIB"),
            "status":   "TRIGGERED",
        }
        sentiment["news_filter_active"] = True
        sentiment["fetched_at"] = datetime.now(WIB).isoformat()
        await set_cached_sentiment(sentiment)
        log.info(f"NewsMonitor: sentiment updated — news filter ACTIVE for {event.get('currency')}")
    except Exception as e:
        log.error(f"NewsMonitor: event processing error — {e}")


async def _check_breaking_news():
    """
    Poll for unexpected high-impact breaking news.
    Currently checks the calendar for new events added since last fetch.
    Extend this with a real news API (e.g. NewsAPI, Forex Factory API) if needed.
    """
    try:
        from src.data.calendar import get_upcoming_events
        from src.cache import get_cached_calendar, set_cached_calendar

        new_events = await asyncio.to_thread(
            get_upcoming_events, ["USD", "EUR", "GBP"], "high"
        )
        cached = await get_cached_calendar() or []
        cached_ids = {str(e.get("event", "")) + str(e.get("time", "")) for e in cached}

        breaking = [
            e for e in new_events
            if str(e.get("event", "")) + str(e.get("time", "")) not in cached_ids
        ]

        if breaking:
            log.warning(f"NewsMonitor: BREAKING NEWS detected — {len(breaking)} new events: {[e.get('event') for e in breaking]}")
            # Merge into cached calendar
            merged = cached + breaking
            await set_cached_calendar(merged)
            # Trigger event processing for each breaking event
            for ev in breaking:
                asyncio.create_task(_on_scheduled_event(ev))
    except Exception as e:
        log.debug(f"NewsMonitor: breaking news check error (non-critical) — {e}")


# ── Job: MT5 Pair Snapshot — skips weekends ────────────────────────────────────

async def job_fetch_mt5_snapshot() -> dict:
    """
    Snapshot technical indicators for MT5 forex/commodity pairs → cache.
    Automatically skipped on Saturday & Sunday (Exness broker closed).
    Service sleeps immediately after completion.
    """
    if _is_market_weekend():
        now = datetime.now(WIB)
        log.info(
            f"Scheduler: MT5 snapshot SKIPPED — {now.strftime('%A')} (weekend, Exness closed). "
            f"Service idle until Monday."
        )
        return {"skipped": True, "reason": "weekend", "day": now.strftime("%A")}

    from src.data.redis_mt5 import get_ohlc
    from src.indicators.technical import compute_indicators
    from src.cache import set_cached_snapshot

    log.info(f"Scheduler: MT5 snapshot started — {datetime.now(WIB).strftime('%H:%M WIB')}")
    snapshot = {}

    async def snap_pair(symbol: str):
        try:
            candles = await get_ohlc(symbol, "H4", limit=200)
            if candles:
                ind = compute_indicators(candles)
                return symbol, {
                    "price":          ind.get("current_price", 0),
                    "recommendation": ind.get("recommendation", "NEUTRAL"),
                    "confidence":     ind.get("confidence", 0),
                    "rsi":            ind.get("RSI", {}).get("value"),
                    "macd_signal":    ind.get("MACD", {}).get("signal"),
                    "ema_signal":     ind.get("EMA", {}).get("signal"),
                    "candles":        len(candles),
                }
        except Exception as e:
            return symbol, {"error": str(e)}
        return symbol, {"error": "no_data"}

    tasks = [snap_pair(p) for p in MORNING_PAIRS]
    results = await asyncio.gather(*tasks)
    for sym, data in results:
        snapshot[sym] = data

    data_out = {
        "pairs":      snapshot,
        "fetched_at": datetime.now(WIB).isoformat(),
        "timeframe":  "H4",
        "source":     "mt5_redis",
    }
    await set_cached_snapshot(data_out)
    log.info(f"Scheduler: MT5 snapshot cached ✓ ({len(snapshot)} pairs) — service now idle")
    return data_out


# ── Job: Morning Briefing — 06:30 WIB ─────────────────────────────────────────

async def job_morning_briefing():
    """
    Full morning briefing — runs at 07:00 WIB.
    Fetches sentiment + fundamental + calendar + VIP Multi-TF snapshot.
    Generates AI briefing and caches for the day.
    """
    log.info("=" * 60)
    log.info(f"Scheduler: MORNING BRIEFING — {datetime.now(WIB).strftime('%Y-%m-%d %H:%M WIB')}")
    log.info("=" * 60)

    # 1. Fetch Basic Data
    sentiment_task = job_fetch_sentiment()
    fundamental_task = job_fetch_fundamental()
    calendar_task = job_fetch_calendar()

    sentiment_data, fundamental_data, calendar_events = await asyncio.gather(
        sentiment_task, fundamental_task, calendar_task,
        return_exceptions=True
    )

    if isinstance(sentiment_data, Exception): sentiment_data = {}
    if isinstance(fundamental_data, Exception): fundamental_data = {}
    if isinstance(calendar_events, Exception): calendar_events = []

    # 2. Fetch VIP Multi-TF Data (XAUUSD, BTC)
    from src.data.redis_mt5 import get_ohlc_smart
    vip_data = {}

    for pair in VIP_PAIRS:
        vip_data[pair] = {}
        for tf in VIP_TIMEFRAMES:
            try:
                candles = await get_ohlc_smart(pair, tf, limit=200)
                vip_data[pair][tf] = {
                    "csv": candles_to_csv(candles),
                    "count": len(candles)
                }
            except Exception as e:
                vip_data[pair][tf] = {"error": str(e)}

    # 3. Fetch DXY Data
    dxy_data = {}
    for tf in DXY_TIMEFRAMES:
        try:
            candles = await get_ohlc_smart("DXY", tf, limit=200)
            dxy_data[tf] = candles_to_csv(candles)
        except Exception:
            pass

    # 4. Fetch Other Pairs (H1, H4 only)
    other_pairs_data = {}
    for pair in MORNING_PAIRS:
        if pair in VIP_PAIRS: continue
        other_pairs_data[pair] = {}
        for tf in ["H1", "H4"]:
            try:
                candles = await get_ohlc_smart(pair, tf, limit=200)
                other_pairs_data[pair][tf] = candles_to_csv(candles)
            except Exception:
                pass

    # 5. Fetch Account Equity (Exness)
    from src.data.redis_mt5 import get_account
    # Assuming user_id 'admin' or first available for briefing context
    # In real scenario, might need to loop per user or use a master account
    account_info = await get_account("admin") # Placeholder for global equity check

    from src.ai import openrouter as ai
    from src.cache import set_cached_briefing

    fear_greed = sentiment_data.get("fear_greed", {})
    macro = fundamental_data.get("macro", {})

    try:
        ai_briefing = await ai.analyze_morning_briefing(
            fear_greed=fear_greed,
            cot_gold=sentiment_data.get("cot_gold", {}),
            cot_dxy=sentiment_data.get("cot_dxy", {}),
            macro=macro,
            calendar_events=calendar_events,
            vip_data=vip_data,
            dxy_data=dxy_data,
            other_pairs=other_pairs_data,
            account_info=account_info
        )
    except Exception as e:
        ai_briefing = f"[AI briefing error: {e}]"
        log.error(f"Scheduler: AI briefing failed — {e}")

    briefing = {
        "date": date.today().isoformat(),
        "generated_at": datetime.now(WIB).isoformat(),
        "type": "daily",
        "ai_briefing": ai_briefing,
        "fear_greed": fear_greed,
        "cot_gold": sentiment_data.get("cot_gold", {}),
        "cot_dxy": sentiment_data.get("cot_dxy", {}),
        "macro": macro,
        "calendar_events": calendar_events[:10] if isinstance(calendar_events, list) else [],
        "source": "scheduled-auto-v3",
        "account_equity": account_info.get("equity") if account_info else None
    }

    await set_cached_briefing(briefing, "daily")
    log.info("Scheduler: Morning briefing complete and cached ✓")
    return briefing


# ── Job: Midday Refresh — 12:00 WIB ───────────────────────────────────────────

async def job_midday_refresh():
    """
    Midday refresh — 12:00 WIB.
    Updates calendar (events change during the day) + sentiment.
    Skipped on weekends. Does NOT re-run expensive AI call.
    """
    if _is_market_weekend():
        log.info("Scheduler: Midday refresh SKIPPED — weekend")
        return

    log.info(f"Scheduler: MIDDAY REFRESH — {datetime.now(WIB).strftime('%H:%M WIB')}")
    await asyncio.gather(
        job_fetch_calendar(),
        job_fetch_sentiment(),
        return_exceptions=True,
    )
    log.info("Scheduler: Midday refresh complete ✓")


# ── Job: Weekly Briefing — Monday 07:00 WIB ───────────────────────────────────

async def job_weekly_briefing():
    """Weekly briefing — Monday 07:00 WIB. Full week-ahead outlook."""
    today = datetime.now(WIB)
    if today.weekday() != 0:   # Only run on Monday
        return

    log.info(f"Scheduler: WEEKLY BRIEFING — {today.strftime('%Y-%m-%d')}")

    sentiment_data, fundamental_data = await asyncio.gather(
        job_fetch_sentiment(),
        job_fetch_fundamental(),
        return_exceptions=True,
    )

    from src.ai import openrouter as ai
    from src.cache import set_cached_briefing

    fear_greed = sentiment_data.get("fear_greed", {}) if isinstance(sentiment_data, dict) else {}
    macro      = fundamental_data.get("macro", {})    if isinstance(fundamental_data, dict) else {}

    try:
        ai_briefing = await ai.analyze_briefing(macro, [], fear_greed, "weekly")
    except Exception as e:
        ai_briefing = f"[Weekly AI error: {e}]"

    briefing = {
        "date":         date.today().isoformat(),
        "generated_at": datetime.now(WIB).isoformat(),
        "type":         "weekly",
        "week":         date.today().strftime("%Y-W%W"),
        "ai_briefing":  ai_briefing,
        "fear_greed":   fear_greed,
        "macro":        macro,
        "source":       "scheduled-auto",
    }

    await set_cached_briefing(briefing, "weekly")
    log.info("Scheduler: Weekly briefing cached ✓")


# ── Scheduler Factory ──────────────────────────────────────────────────────────

def create_scheduler() -> AsyncIOScheduler:
    """Create and configure APScheduler with all GAS jobs."""
    scheduler = AsyncIOScheduler(timezone=WIB)

    # 05:00 WIB — Economic calendar (ecocal) + news monitor start
    scheduler.add_job(
        job_fetch_calendar,
        CronTrigger(hour=5, minute=0, timezone=WIB),
        id="calendar_fetch",
        name="Economic Calendar Fetch (05:00 WIB)",
        replace_existing=True,
        misfire_grace_time=600,
    )

    # 07:00 WIB — Full morning briefing
    scheduler.add_job(
        job_morning_briefing,
        CronTrigger(hour=7, minute=0, timezone=WIB),
        id="morning_briefing",
        name="Morning Full Briefing (07:00 WIB)",
        replace_existing=True,
        misfire_grace_time=600,
    )

    # 07:00 WIB — Macro/fundamental data (TradingEconomics)
    scheduler.add_job(
        job_fetch_fundamental,
        CronTrigger(hour=7, minute=0, timezone=WIB),
        id="fundamental_fetch",
        name="Fundamental Macro Fetch (07:00 WIB)",
        replace_existing=True,
        misfire_grace_time=600,
    )

    # 12:00 WIB — Midday calendar + sentiment refresh
    scheduler.add_job(
        job_midday_refresh,
        CronTrigger(hour=12, minute=0, timezone=WIB),
        id="midday_refresh",
        name="Midday Data Refresh (12:00 WIB)",
        replace_existing=True,
        misfire_grace_time=300,
    )

    # Monday 07:00 WIB — Weekly briefing
    scheduler.add_job(
        job_weekly_briefing,
        CronTrigger(day_of_week="mon", hour=7, minute=0, timezone=WIB),
        id="weekly_briefing",
        name="Weekly Market Outlook (Mon 07:00 WIB)",
        replace_existing=True,
        misfire_grace_time=900,
    )

    return scheduler


# ── Global scheduler instance ──────────────────────────────────────────────────

_scheduler: Optional[AsyncIOScheduler] = None


async def start_scheduler(run_now: bool = True):
    """Start the scheduler. Call from FastAPI lifespan."""
    global _scheduler
    _scheduler = create_scheduler()
    _scheduler.start()
    log.info(
        "Scheduler started ✓ Jobs:\n"
        "  05:00 WIB — Calendar (ecocal) + news monitor\n"
        "  06:30 WIB — Morning briefing\n"
        "  07:00 WIB — Fundamental/macro (TradingEconomics)\n"
        "  12:00 WIB — Midday refresh\n"
        "  Mon 07:00 WIB — Weekly briefing\n"
        "  Weekend: MT5 snapshot skipped (Exness closed)"
    )

    if run_now:
        from src.cache import get_cached_briefing
        existing = await get_cached_briefing("daily")
        if existing:
            log.info(f"Scheduler: Today's briefing already cached ({existing.get('generated_at', 'unknown')})")
        else:
            log.info("Scheduler: No briefing cache — running morning briefing on startup...")
            asyncio.create_task(job_morning_briefing())


async def stop_scheduler():
    """Stop the scheduler. Call from FastAPI lifespan shutdown."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        log.info("Scheduler stopped ✓")


def get_scheduler_status() -> dict:
    """Get current scheduler status and next run times."""
    if not _scheduler or not _scheduler.running:
        return {"status": "stopped", "weekend": _is_market_weekend()}

    jobs = []
    for job in _scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            "id":           job.id,
            "name":         job.name,
            "next_run_wib": next_run.astimezone(WIB).strftime("%Y-%m-%d %H:%M WIB") if next_run else None,
        })

    return {
        "status":            "running",
        "timezone":          "Asia/Jakarta (WIB = UTC+7)",
        "is_weekend":        _is_market_weekend(),
        "mt5_active":        not _is_market_weekend(),
        "current_time_wib":  datetime.now(WIB).strftime("%Y-%m-%d %H:%M WIB"),
        "jobs":              jobs,
    }
