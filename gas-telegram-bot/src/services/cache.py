"""
GAS Bot — Smart Cache Service
TTLs per job type:
  signal:{pair}:{style}  → 30s  (fresh market signal)
  scanner:{key}          → 60s  (multi-pair scan result)
  feed:{key}             → 300s (news, calendar)
"""
import json
from typing import Optional, Any

from src.services.redis_client import get_redis

_TTL = {
    "signal":  30,
    "scanner": 60,
    "feed":    300,
}


# ── Signal cache ─────────────────────────────────────────────────────────────

async def get_signal(pair: str, style: str) -> Optional[dict]:
    r = await get_redis()
    raw = await r.get(f"cache:signal:{pair.upper()}:{style.lower()}")
    return json.loads(raw) if raw else None


async def set_signal(pair: str, style: str, data: dict, ttl: int = None) -> None:
    r = await get_redis()
    await r.set(
        f"cache:signal:{pair.upper()}:{style.lower()}",
        json.dumps(data),
        ex=ttl if ttl is not None else _TTL["signal"],
    )


async def invalidate_signal(pair: str, style: str) -> None:
    r = await get_redis()
    await r.delete(f"cache:signal:{pair.upper()}:{style.lower()}")


# ── Scanner cache ─────────────────────────────────────────────────────────────

async def get_scanner(key: str) -> Optional[Any]:
    r = await get_redis()
    raw = await r.get(f"cache:scanner:{key}")
    return json.loads(raw) if raw else None


async def set_scanner(key: str, data: Any) -> None:
    r = await get_redis()
    await r.set(f"cache:scanner:{key}", json.dumps(data), ex=_TTL["scanner"])


# ── Feed cache ─────────────────────────────────────────────────────────────────

async def get_feed(feed_key: str) -> Optional[Any]:
    r = await get_redis()
    raw = await r.get(f"cache:feed:{feed_key}")
    return json.loads(raw) if raw else None


async def set_feed(feed_key: str, data: Any) -> None:
    r = await get_redis()
    await r.set(f"cache:feed:{feed_key}", json.dumps(data), ex=_TTL["feed"])
