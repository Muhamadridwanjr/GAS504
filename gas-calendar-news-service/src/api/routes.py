from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.db.repositories.event_repo import EventRepo
from src.db.repositories.news_repo import NewsRepo
from src.core.calendar_service import CalendarService
from src.core.news_service import NewsService
from src.core.summary_generator import generate_event_summary
from src.cache.redis_cache import RedisCache
from src.api.models import EventResponse, SummaryResponse

router = APIRouter(tags=["Calendar"])

@router.get("/calendar", response_model=EventResponse)
async def get_calendar(country: str | None = None, importance: str | None = None,
                       from_date: str | None = None, to_date: str | None = None,
                       limit: int = 100, db: AsyncSession = Depends(get_db)):
    cache = RedisCache(); await cache.connect()
    repo = EventRepo(db)
    svc = CalendarService(repo, cache)
    fd = datetime.fromisoformat(from_date) if from_date else None
    td = datetime.fromisoformat(to_date) if to_date else None
    result = await svc.get_events(country, importance, fd, td, limit)
    await cache.close()
    return EventResponse(**result)

@router.get("/news")
async def get_news(limit: int = 50, db: AsyncSession = Depends(get_db)):
    repo = NewsRepo(db)
    svc = NewsService(repo)
    return await svc.get_news(limit)

@router.get("/news/latest")
async def get_news_latest(limit: int = 30, db: AsyncSession = Depends(get_db)):
    """Alias used by gas-terminal-backend. Returns latest N news items as list."""
    repo = NewsRepo(db)
    svc = NewsService(repo)
    result = await svc.get_news(limit)
    # Normalise to a plain list that terminal-backend expects
    if isinstance(result, dict):
        items = result.get("news", result.get("items", []))
    elif isinstance(result, list):
        items = result
    else:
        items = []
    return items

@router.get("/summary", response_model=SummaryResponse)
async def get_summary(from_date: str = Query(...), to_date: str = Query(...), db: AsyncSession = Depends(get_db)):
    repo = EventRepo(db)
    fd = datetime.fromisoformat(from_date); td = datetime.fromisoformat(to_date)
    rows = await repo.get_events(from_date=fd, to_date=td, limit=500)
    data = [{"country": r.country, "title": r.title, "importance": r.importance,
             "actual_value": r.actual_value, "forecast_value": r.forecast_value, "previous_value": r.previous_value}
            for r in rows]
    return SummaryResponse(summary=generate_event_summary(data), event_count=len(data))

@router.get("/analysis")
async def get_calendar_analysis():
    """Return latest AI calendar analysis from Redis cache."""
    cache = RedisCache(); await cache.connect()
    try:
        raw = await cache.get("calendar:analysis")
        if not raw:
            return {"status": "no_data", "message": "AI analysis belum tersedia. Jalankan scheduler jam 05:05 WIB."}
        import json
        try:
            data = json.loads(raw)
            if isinstance(data, str):
                data = json.loads(data)
        except Exception:
            data = {}
        return {"status": "ok", "data": data}
    finally:
        await cache.close()

@router.post("/ingest/run", status_code=202)
async def trigger_ingest(start_date: str | None = None, end_date: str | None = None, db: AsyncSession = Depends(get_db)):
    from src.ingestion.ecocal_worker import fetch_calendar_events
    events = await fetch_calendar_events(db, start_date=start_date, end_date=end_date)
    return {"status": "triggered", "events_fetched": len(events), "period": {"start": start_date, "end": end_date}}
