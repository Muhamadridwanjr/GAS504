"""API routes for fundamental data."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.db.repositories.fundamental_repo import FundamentalRepo
from src.core.data_service import DataService
from src.core.summary_generator import generate_fundamental_summary
from src.api.models import FundamentalResponse, FundamentalSummaryResponse, FundamentalCreateRequest, FundamentalDataPoint
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Fundamental"])

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
    if not ok: raise HTTPException(status_code=404, detail="Record not found")
