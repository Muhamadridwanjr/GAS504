"""
Calendar data — reads from Redis cache (populated by gas-calendar-news-service).
Falls back to direct ecocal fetch if Redis unavailable.
"""
import json
import os
from typing import List, Dict

REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
CALENDAR_NEWS_URL = os.getenv("CALENDAR_NEWS_URL", "http://gas-calendar-news-service:9601")


def get_upcoming_events(currencies: List[str] = None, impact: str = "high") -> List[Dict]:
    """
    Return today's economic events.
    Priority: 1) Redis cache (calendar:analysis from calendar-news-service)
              2) Direct HTTP call to calendar-news-service /calendar endpoint
              3) Fallback empty list
    """
    if currencies is None:
        currencies = {"USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CAD", "CHF", "CNY"}
    else:
        currencies = set(c.upper() for c in currencies)

    IMPACT_PRIORITY = {"HIGH", "MEDIUM"} if impact != "high" else {"HIGH"}

    # 1. Try Redis cache
    try:
        import redis
        r = redis.from_url(REDIS_URL, decode_responses=True)
        raw = r.get("calendar:analysis")
        if raw:
            data = json.loads(raw)
            if isinstance(data, str):
                data = json.loads(data)
            events = data.get("priority_events", [])
            results = []
            for ev in events:
                country   = str(ev.get("country", "")).upper()
                imp       = str(ev.get("importance", "")).upper()
                if country not in currencies:
                    continue
                if imp not in IMPACT_PRIORITY:
                    continue
                results.append({
                    "time":     str(ev.get("time_utc", "")),
                    "currency": country,
                    "event":    ev.get("title", ""),
                    "impact":   imp,
                    "forecast": str(ev.get("forecast", "-") or "-"),
                    "previous": str(ev.get("previous", "-") or "-"),
                    "actual":   str(ev.get("actual",   "-") or "-"),
                    "bias":     ev.get("market_bias", "NEUTRAL"),
                })
            if results:
                return results
    except Exception:
        pass

    # 2. Try calendar-news-service HTTP API
    try:
        import requests
        resp = requests.get(
            f"{CALENDAR_NEWS_URL}/calendar",
            params={"importance": "high", "limit": 50},
            headers={"X-Internal-Key": "gas-internal-secret-key"},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            events = data.get("events", [])
            results = []
            for ev in events:
                country = str(ev.get("country", "")).upper()
                imp     = str(ev.get("importance", "")).upper()
                if country not in currencies:
                    continue
                if imp not in IMPACT_PRIORITY:
                    continue
                results.append({
                    "time":     str(ev.get("time_utc", "")),
                    "currency": country,
                    "event":    ev.get("title", ""),
                    "impact":   imp,
                    "forecast": str(ev.get("forecast_value", "-") or "-"),
                    "previous": str(ev.get("previous_value", "-") or "-"),
                    "actual":   str(ev.get("actual_value",   "-") or "-"),
                    "bias":     "NEUTRAL",
                })
            if results:
                return results
    except Exception:
        pass

    return []
