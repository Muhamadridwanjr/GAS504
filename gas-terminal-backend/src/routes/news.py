"""
GET /terminal/news – Latest market news from calendar-news service.
Falls back to livenews.md if live DB data unavailable.
"""
import os, re
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()

WIB = timezone(timedelta(hours=7))
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _fallback_from_md() -> list[dict]:
    """Read livenews.md and return list of news dicts."""
    path = os.path.join(DATA_DIR, "livenews.md")
    items = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("- ") or line.startswith("<!--"):
                    continue
                line = line[2:].strip()
                m = re.match(r"\[(\d{2}:\d{2})\]\s*(.*)", line)
                if not m:
                    continue
                time_str, rest = m.group(1), m.group(2)
                parts = [p.strip() for p in rest.split("|")]
                items.append({
                    "title":     parts[0] if parts else rest,
                    "source":    parts[1] if len(parts) > 1 else "GAS Feed",
                    "impact":    (parts[2].upper() if len(parts) > 2 else "LOW"),
                    "time":      time_str,
                    "published_at": datetime.now(WIB).isoformat(),
                })
    except Exception:
        pass
    return items


@router.get("/terminal/news")
async def get_news():
    """Get latest market news. Falls back to livenews.md if service unavailable."""
    data = await fetch_json(f"{settings.CALENDAR_NEWS_URL}/news/latest", timeout=8.0)

    # Use live DB data if available
    if isinstance(data, list) and len(data) > 0:
        return {
            "status": "ok",
            "source": "live",
            "news": data,
            "count": len(data),
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
        }

    # Fallback to livenews.md
    fallback = _fallback_from_md()
    return {
        "status":  "ok" if fallback else "unavailable",
        "source":  "file" if fallback else "none",
        "news":    fallback,
        "count":   len(fallback),
        "timestamp": int(datetime.now(timezone.utc).timestamp()),
        "note": "Menggunakan data livenews.md (fallback). Update file untuk berita terkini.",
    }
