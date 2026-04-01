"""
Redis cache helpers for pre-fetched market data.
Keys:
  cache:briefing:daily:{YYYY-MM-DD}  → daily morning briefing (TTL 28h)
  cache:briefing:weekly:{YYYY-WNN}   → weekly briefing (TTL 7d)
  cache:sentiment:latest             → COT + Fear/Greed (TTL 25h)
  cache:fundamental:latest           → macro data (TTL 25h)
  cache:calendar:latest              → economic events (TTL 12h)
  cache:snapshot:latest              → MT5 pair snapshots (TTL 4h)
"""
import json
import os
from typing import Optional, Any
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_redis = None


async def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


async def cache_set(key: str, value: Any, ttl_seconds: int = 86400) -> None:
    r = await get_redis()
    await r.set(key, json.dumps(value, default=str), ex=ttl_seconds)


async def cache_get(key: str) -> Optional[Any]:
    r = await get_redis()
    raw = await r.get(key)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return None
    return None


async def cache_delete(key: str) -> None:
    r = await get_redis()
    await r.delete(key)


async def get_cached_briefing(briefing_type: str = "daily") -> Optional[dict]:
    from datetime import date, datetime
    if briefing_type == "weekly":
        week_key = date.today().strftime("%Y-W%W")
        return await cache_get(f"cache:briefing:weekly:{week_key}")
    else:
        today = date.today().isoformat()
        return await cache_get(f"cache:briefing:daily:{today}")


async def set_cached_briefing(data: dict, briefing_type: str = "daily") -> None:
    from datetime import date
    if briefing_type == "weekly":
        week_key = date.today().strftime("%Y-W%W")
        await cache_set(f"cache:briefing:weekly:{week_key}", data, ttl_seconds=7 * 24 * 3600)
    else:
        today = date.today().isoformat()
        await cache_set(f"cache:briefing:daily:{today}", data, ttl_seconds=28 * 3600)


async def get_cached_sentiment() -> Optional[dict]:
    return await cache_get("cache:sentiment:latest")


async def set_cached_sentiment(data: dict) -> None:
    await cache_set("cache:sentiment:latest", data, ttl_seconds=25 * 3600)


async def get_cached_fundamental() -> Optional[dict]:
    return await cache_get("cache:fundamental:latest")


async def set_cached_fundamental(data: dict) -> None:
    await cache_set("cache:fundamental:latest", data, ttl_seconds=25 * 3600)


async def get_cached_calendar() -> Optional[list]:
    return await cache_get("cache:calendar:latest")


async def set_cached_calendar(data: list) -> None:
    await cache_set("cache:calendar:latest", data, ttl_seconds=12 * 3600)


async def get_cached_snapshot() -> Optional[dict]:
    return await cache_get("cache:snapshot:latest")


async def set_cached_snapshot(data: dict) -> None:
    await cache_set("cache:snapshot:latest", data, ttl_seconds=4 * 3600)
