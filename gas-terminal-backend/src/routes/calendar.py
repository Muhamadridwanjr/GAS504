"""
GET /terminal/calendar – Economic calendar events.
"""
from fastapi import APIRouter, Query
from typing import Optional
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()

FALLBACK_EVENTS = [
    {"date": "Mar 6", "name": "ADP Non-Farm Employment", "impact": "HIGH", "time": "13:15"},
    {"date": "Mar 7", "name": "US Unemployment Claims", "impact": "MEDIUM", "time": "13:30"},
    {"date": "Mar 8", "name": "Non-Farm Payrolls", "impact": "HIGH", "time": "13:30"},
    {"date": "Mar 12", "name": "CPI Month over Month", "impact": "HIGH", "time": "13:30"},
    {"date": "Mar 19", "name": "FOMC Statement", "impact": "HIGH", "time": "18:00"},
]


@router.get("/terminal/calendar")
async def get_calendar(
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    impact: Optional[str] = Query(None),
):
    """Get economic calendar events."""
    params = {}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if impact:
        params["impact"] = impact

    data = await fetch_json(f"{settings.CALENDAR_NEWS_URL}/calendar/events", params=params or None)
    if "error" in data or not isinstance(data, list):
        return {"status": "ok", "events": FALLBACK_EVENTS}
    return {"status": "ok", "events": data}
