"""
GET /terminal/calendar – Economic calendar events.
Proxies to gas-calendar-news-service with proper params.
"""
from fastapi import APIRouter, Query
from typing import Optional
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()


@router.get("/terminal/calendar")
async def get_calendar(
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    importance: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    limit: int = Query(200),
):
    """Proxy calendar events from gas-calendar-news-service."""
    params = {"limit": limit}
    if from_date:
        params["from_date"] = from_date
    if to_date:
        params["to_date"] = to_date
    if importance:
        params["importance"] = importance
    if country:
        params["country"] = country

    headers = {"X-Internal-Key": "gas-internal-secret-key"}
    data = await fetch_json(
        f"{settings.CALENDAR_NEWS_URL}/calendar",
        params=params,
        headers=headers,
    )
    if isinstance(data, dict) and "data" in data:
        return data
    if isinstance(data, dict) and "error" in data:
        return {"total": 0, "data": []}
    return {"total": 0, "data": []}
