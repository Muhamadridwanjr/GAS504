"""
Scheduler for tedata ingestion from Trading Economics.

Schedule : 05:00 WIB (Asia/Jakarta) daily.
Window   : 05:00 – ~06:00 WIB (headless Firefox active only during scrape).
After run: browser closed, service sleeps until next 05:00 WIB.

Pipeline per run:
  1. Launch headless Firefox → scrape 20+ macro indicators via tedata
  2. Store dashboard snapshot in Redis  (macro:dashboard, TTL 25h)
  3. Run AI macro analysis → store in Redis  (macro:analysis, TTL 25h)
  4. Log sleep window, service idle until next scheduled run

On startup: checks Redis cache. If today's data already present → skips scrape.
Manual trigger: POST /macro/refresh
"""
from __future__ import annotations
import asyncio
import json
import datetime
from concurrent.futures import ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from src.lib.logger import get_logger

logger = get_logger(__name__)
_scheduler: AsyncIOScheduler | None = None

WIB = pytz.timezone("Asia/Jakarta")

# Currencies we build analysis for
PRIORITY_IMPACTS = {"VERY_HIGH", "HIGH"}

# ─── AI MACRO ANALYSIS ───────────────────────────────────────────────────────

_REGION_CURRENCY = {
    "USA":      "USD",
    "Eurozone": "EUR",
    "Japan":    "JPY",
    "UK":       "GBP",
    "China":    "CNY",
}


def _build_macro_analysis(results: list[dict]) -> dict:
    """
    Build AI macro analysis from scraped indicator results.
    Scores market sentiment per currency, determines market regime,
    and generates a plain-text macro narrative.
    """
    currency_signals: dict[str, dict] = {
        "USD": {"bullish": 0, "bearish": 0, "neutral": 0},
        "EUR": {"bullish": 0, "bearish": 0, "neutral": 0},
        "JPY": {"bullish": 0, "bearish": 0, "neutral": 0},
        "GBP": {"bullish": 0, "bearish": 0, "neutral": 0},
        "CNY": {"bullish": 0, "bearish": 0, "neutral": 0},
    }

    inflation_pressure = 0   # positive = elevated
    growth_pressure    = 0   # positive = expanding

    for r in results:
        actual   = r.get("actual")
        previous = r.get("previous")
        key      = r.get("key", "")
        region   = r.get("region", "")
        impact   = r.get("impact", "")

        if actual is None or previous is None:
            continue
        if impact not in PRIORITY_IMPACTS:
            continue

        currency = _REGION_CURRENCY.get(region)
        change   = actual - previous

        # ── Classify signal direction ──────────────────────────────────────
        if key in ("US_CPI", "US_CORE_CPI", "EU_CPI", "UK_CPI", "JP_CPI"):
            inflation_pressure += 1 if change > 0 else -1
            signal = "bearish" if change > 0 else "bullish"   # high inflation = hawkish = bearish FX

        elif key in ("US_FED_RATE", "ECB_RATE", "BOE_RATE", "JP_BOJ_RATE"):
            if change > 0:
                signal = "bullish"
            elif change < 0:
                signal = "bearish"
            else:
                signal = "neutral"

        elif key == "US_NFP":
            signal = "bullish" if change > 0 else "bearish"
            growth_pressure += 1 if change > 0 else -1

        elif key in ("US_MFG_PMI", "EU_MFG_PMI", "GLOBAL_MFG_PMI", "CHINA_MFG_PMI"):
            signal = "bullish" if actual >= 50 else "bearish"
            growth_pressure += 1 if actual >= 50 else -1

        elif key in ("US_GDP", "EU_GDP", "UK_GDP"):
            signal = "bullish" if change >= 0 else "bearish"
            growth_pressure += 1 if change > 0 else -1

        elif key == "US_UNEMPLOYMENT":
            signal = "bearish" if change > 0 else "bullish"

        elif key == "EIA_CRUDE":
            signal = "bearish" if change > 0 else "bullish"   # inventory build = bearish oil

        else:
            signal = "neutral"

        if currency and currency in currency_signals:
            currency_signals[currency][signal] += 1

    # ── Build 0-100 score per currency ────────────────────────────────────
    currency_scores: dict = {}
    for ccy, counts in currency_signals.items():
        total = counts["bullish"] + counts["bearish"] + counts["neutral"]
        if total == 0:
            currency_scores[ccy] = {"score": 50, "bias": "NEUTRAL", "signals": 0}
            continue
        score = int((counts["bullish"] / total) * 100)
        bias  = "BULLISH" if score >= 65 else ("BEARISH" if score <= 35 else "NEUTRAL")
        currency_scores[ccy] = {
            "score": score,
            "bias": bias,
            "signals": total,
            "breakdown": counts,
        }

    # ── Macro regime ──────────────────────────────────────────────────────
    if growth_pressure >= 2 and inflation_pressure <= 0:
        market_regime = "RISK_ON";   overall_risk = "LOW"
    elif inflation_pressure >= 3 or growth_pressure <= -2:
        market_regime = "RISK_OFF";  overall_risk = "HIGH"
    elif inflation_pressure >= 2:
        market_regime = "STAGFLATION_RISK"; overall_risk = "HIGH"
    else:
        market_regime = "MIXED";     overall_risk = "MODERATE"

    # ── Plain-text narrative ──────────────────────────────────────────────
    usd_bias = currency_scores.get("USD", {}).get("bias", "NEUTRAL")
    parts = [
        f"USD {usd_bias} — "
        + ("hawkish Fed backdrop, DXY strength expected." if usd_bias == "BULLISH"
           else "dovish macro environment, DXY under pressure." if usd_bias == "BEARISH"
           else "mixed signals, await next catalyst."),
    ]
    if growth_pressure >= 1:
        parts.append("Global growth data tilts positive — risk assets may find support.")
    elif growth_pressure <= -1:
        parts.append("Growth momentum slowing — defensive positioning advised.")
    if inflation_pressure >= 2:
        parts.append("Inflation elevated — rate-cut expectations receding, bearish bonds.")
    elif inflation_pressure <= -1:
        parts.append("Inflation cooling — window opens for central bank easing.")

    return {
        "generated_at":       datetime.datetime.now(WIB).isoformat(),
        "market_regime":      market_regime,
        "overall_risk":       overall_risk,
        "currency_scores":    currency_scores,
        "growth_pressure":    growth_pressure,
        "inflation_pressure": inflation_pressure,
        "narrative":          " ".join(parts) or "Macro data is mixed. Monitor upcoming releases.",
        "indicators_analyzed": len(results),
    }


# ─── PIPELINE ────────────────────────────────────────────────────────────────

async def _run_scrape_job():
    """
    Full scrape pipeline — runs at 05:00 WIB.

    1. Launch headless Firefox via tedata (ProcessPoolExecutor)
    2. Fetch all macro indicators
    3. Store macro:dashboard snapshot in Redis
    4. Run AI analysis → store macro:analysis in Redis
    5. Log sleep until next 05:00 WIB
    """
    from src.ingestion.te_scraper import scrape_all_sync
    from src.cache.redis_cache import RedisCache

    now_wib = datetime.datetime.now(WIB).strftime("%H:%M WIB")
    logger.info("=== [PIPELINE START] TE Macro Scrape (%s) ===", now_wib)
    loop = asyncio.get_event_loop()

    try:
        # ── 1: Scrape ──────────────────────────────────────────────────────
        logger.info("[1/3] Launching headless Firefox via tedata (ProcessPoolExecutor)...")
        with ProcessPoolExecutor(max_workers=1) as executor:
            results = await loop.run_in_executor(executor, scrape_all_sync, None)
        logger.info(
            "[1/3] Scrape done — %d indicators fetched. Firefox process closed.",
            len(results) if results else 0,
        )

        if not results:
            logger.warning("[1/3] No results from TE scrape — keeping existing cache.")
            return

        cache = RedisCache()
        await cache.connect()

        # ── 2: Store dashboard ─────────────────────────────────────────────
        logger.info("[2/3] Storing macro dashboard to Redis (TTL 25h)...")
        payload = {
            "last_updated": datetime.datetime.now(WIB).isoformat(),
            "indicators":   results,
        }
        await cache.set("macro:dashboard", json.dumps(payload), ttl=90000)

        # ── 3: AI Analysis ─────────────────────────────────────────────────
        logger.info("[3/3] Running AI macro analysis...")
        analysis = _build_macro_analysis(results)
        await cache.set("macro:analysis", json.dumps(analysis), ttl=90000)
        logger.info(
            "[3/3] AI analysis complete — regime: %s | risk: %s | USD: %s",
            analysis["market_regime"],
            analysis["overall_risk"],
            analysis["currency_scores"].get("USD", {}).get("bias", "N/A"),
        )

        await cache.close()

        # ── Done — log next window ─────────────────────────────────────────
        next_run = (
            datetime.datetime.now(WIB)
            .replace(hour=5, minute=0, second=0, microsecond=0)
            + datetime.timedelta(days=1)
        )
        logger.info(
            "=== [PIPELINE COMPLETE] %d indicators stored. "
            "Headless Firefox closed. Service sleeping until %s WIB. ===",
            len(results),
            next_run.strftime("%Y-%m-%d %H:%M"),
        )

    except Exception as e:
        logger.error("[PIPELINE ERROR] %s", e)


async def _check_and_run_on_startup():
    """
    On startup: skip scrape if Redis already has today's fresh data.
    If stale or empty → run the pipeline once immediately.
    """
    from src.cache.redis_cache import RedisCache

    cache = RedisCache()
    await cache.connect()
    try:
        cached = await cache.get("macro:dashboard")
        if cached:
            try:
                data = json.loads(cached) if isinstance(cached, str) else cached
            except Exception:
                data = cached
            last_updated = data.get("last_updated", "") if isinstance(data, dict) else ""
            today_wib    = datetime.datetime.now(WIB).date().isoformat()
            if last_updated.startswith(today_wib):
                logger.info(
                    "Startup: cache is fresh (updated %s) — skipping scrape. "
                    "Next run: 05:00 WIB tomorrow.",
                    last_updated[:19],
                )
                return
        logger.info("Startup: no fresh cache found — running initial scrape once...")
    finally:
        await cache.close()

    await _run_scrape_job()


# ─── SCHEDULER LIFECYCLE ─────────────────────────────────────────────────────

def start_scheduler():
    global _scheduler
    _scheduler = AsyncIOScheduler(timezone=WIB)

    # Daily at 05:00 WIB
    _scheduler.add_job(
        _run_scrape_job,
        CronTrigger(hour=5, minute=0, timezone=WIB),
        id="te_scrape_daily",
        name="TE Macro Scrape (05:00 WIB)",
        replace_existing=True,
        misfire_grace_time=1800,
    )
    _scheduler.start()

    asyncio.get_event_loop().create_task(_check_and_run_on_startup())

    now_wib = datetime.datetime.now(WIB).strftime("%H:%M WIB")
    logger.info(
        "Fundamental scheduler started — scrape at 05:00 WIB daily (current: %s). "
        "Headless Firefox activates only during the 05:00-06:00 WIB window.",
        now_wib,
    )


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)


async def run_ingestion_cycle():
    """Manual trigger for a single scrape cycle (via POST /macro/refresh)."""
    await _run_scrape_job()
