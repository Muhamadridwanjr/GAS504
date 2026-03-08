"""API routes for fundamental data."""
from __future__ import annotations
import json
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.db.repositories.fundamental_repo import FundamentalRepo
from src.core.data_service import DataService
from src.core.summary_generator import generate_fundamental_summary
from src.api.models import (
    FundamentalResponse, FundamentalSummaryResponse, FundamentalCreateRequest,
    FundamentalDataPoint, MacroDashboardResponse, MacroIndicator, MacroHistoryPoint,
)
from src.ingestion.te_scraper import TE_INDICATORS, _generate_ai_note
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Fundamental"])


# ─── EXISTING ENDPOINTS ───────────────────────────────────────────────────────

@router.get("/fundamental/{symbol}", response_model=FundamentalResponse)
async def get_fundamental(symbol: str, indicator: str = Query(...), from_time: int | None = None,
                          to_time: int | None = None, limit: int = 100, db: AsyncSession = Depends(get_db)):
    from src.cache.redis_cache import RedisCache
    cache = RedisCache()
    await cache.connect()
    repo = FundamentalRepo(db)
    svc = DataService(repo, cache)
    result = await svc.get_data(symbol.upper(), indicator, from_time, to_time, limit)
    await cache.close()
    return FundamentalResponse(symbol=result["symbol"], indicator=result["indicator"],
        data=[FundamentalDataPoint(**d) for d in result["data"]])


@router.get("/fundamental/{symbol}/summary", response_model=FundamentalSummaryResponse)
async def get_summary(symbol: str, indicator: str = Query(...), period: str = "month",
                      db: AsyncSession = Depends(get_db)):
    repo = FundamentalRepo(db)
    rows = await repo.get_data(symbol.upper(), indicator, limit=100)
    data = [{"time": r.time, "value": r.value, "unit": r.unit} for r in rows]
    summary = generate_fundamental_summary(symbol.upper(), indicator, data, period)
    return FundamentalSummaryResponse(symbol=symbol.upper(), indicator=indicator, summary=summary, period=period)


@router.post("/fundamental", status_code=201)
async def create_fundamental(req: FundamentalCreateRequest, db: AsyncSession = Depends(get_db)):
    repo = FundamentalRepo(db)
    obj = await repo.upsert(req.symbol.upper(), req.indicator, req.time, req.value, req.unit, req.source)
    return {"id": obj.id, "symbol": obj.symbol, "indicator": obj.indicator}


@router.delete("/fundamental/{record_id}", status_code=204)
async def delete_fundamental(record_id: int, db: AsyncSession = Depends(get_db)):
    repo = FundamentalRepo(db)
    ok = await repo.delete(record_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Record not found")


# ─── MACRO DASHBOARD ──────────────────────────────────────────────────────────

@router.get("/macro/dashboard", response_model=MacroDashboardResponse, tags=["Macro"])
async def get_macro_dashboard(background_tasks: BackgroundTasks):
    """
    Returns the latest macro indicator snapshot from Redis cache.
    The cache is populated every 6 hours by the tedata scheduler.
    Falls back to metadata-only response if cache is empty (first run).
    """
    from src.cache.redis_cache import RedisCache
    cache = RedisCache()
    await cache.connect()

    try:
        cached = await cache.get("macro:dashboard")
        if cached:
            data = json.loads(cached)
            indicators = [MacroIndicator(**ind) for ind in data.get("indicators", [])]
            return MacroDashboardResponse(
                last_updated=data.get("last_updated", ""),
                indicators=indicators,
            )
    except Exception as e:
        logger.warning("Cache read error: %s", e)
    finally:
        await cache.close()

    # Cache miss — return metadata skeleton with nulls + trigger background scrape
    background_tasks.add_task(_trigger_scrape_background)
    now = datetime.datetime.utcnow().isoformat()
    indicators = [
        MacroIndicator(
            key=key,
            label=meta["label"],
            region=meta["region"],
            assets=meta["assets"],
            tier=meta["tier"],
            impact=meta["impact"],
            unit=meta["unit"],
            period=meta["period"],
            actual=None,
            previous=None,
            status="loading",
            ai_notes="Data sedang diambil dari Trading Economics. Harap tunggu beberapa menit...",
            scraped_at=None,
        )
        for key, meta in TE_INDICATORS.items()
    ]
    return MacroDashboardResponse(last_updated=now, indicators=indicators)


@router.post("/macro/refresh", tags=["Macro"])
async def trigger_macro_refresh(background_tasks: BackgroundTasks):
    """Manually trigger a full Trading Economics scrape cycle."""
    background_tasks.add_task(_trigger_scrape_background)
    return {"status": "ok", "message": "Scrape cycle started in background"}


async def _trigger_scrape_background():
    """Kick off the scrape job without blocking the response."""
    try:
        from src.ingestion.scheduler import run_ingestion_cycle
        await run_ingestion_cycle()
    except Exception as e:
        logger.error("Background scrape failed: %s", e)
