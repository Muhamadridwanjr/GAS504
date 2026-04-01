"""
POST /terminal/screener – Run GAS market screener across symbols.
GET  /terminal/screener/symbols – List supported symbols.

Anti-thundering-herd pattern:
  - Shared Redis cache (TTL 30s) keyed by request body hash.
  - Distributed Redis lock prevents concurrent identical requests from
    all hitting gas-screener-service simultaneously.
  - Lock holders run the actual screener; waiters get the cached result.
"""
import asyncio
import hashlib
import json
import os

import redis.asyncio as aioredis
from fastapi import APIRouter

from src.config import settings
from src.services.client import fetch_json

router = APIRouter()

REDIS_URL        = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
SCREENER_TTL     = 30          # seconds — screener result cache duration
LOCK_TTL         = 20          # seconds — distributed lock TTL (auto-expire on crash)
LOCK_POLL_DELAY  = 0.3         # seconds — poll interval while waiting for lock
LOCK_MAX_WAIT    = 15.0        # seconds — max time a waiter will wait for lock holder

_redis = None


async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


def _cache_key(body: dict) -> str:
    body_str = json.dumps(body, sort_keys=True)
    return "screener:cache:" + hashlib.sha256(body_str.encode()).hexdigest()[:16]


def _lock_key(cache_key: str) -> str:
    return cache_key.replace("screener:cache:", "screener:lock:")


@router.post("/terminal/screener")
async def run_screener(body: dict = None):
    """
    Run the GAS screener engine with shared cache + distributed lock.
    Concurrent requests with the same filter body will share one upstream call.
    """
    body = body or {}
    cache_key = _cache_key(body)
    lock_key  = _lock_key(cache_key)

    try:
        r = await _get_redis()

        # ── Cache hit — serve immediately ────────────────────────────────────
        cached = await r.get(cache_key)
        if cached:
            data = json.loads(cached)
            data["_cached"] = True
            return {"status": "ok", **data}

        # ── Try to acquire distributed lock ───────────────────────────────────
        acquired = await r.set(lock_key, "1", ex=LOCK_TTL, nx=True)

        if acquired:
            # ── Lock holder: call screener, cache result ──────────────────────
            try:
                data = await fetch_json(
                    f"{settings.SCREENER_URL}/screener",
                    method="POST",
                    json_body=body,
                    timeout=15.0,
                )
                if "error" not in data:
                    await r.setex(cache_key, SCREENER_TTL, json.dumps(data))
            finally:
                await r.delete(lock_key)
        else:
            # ── Waiter: poll until lock is released (or cache appears) ────────
            waited = 0.0
            data = {"error": "timeout"}
            while waited < LOCK_MAX_WAIT:
                await asyncio.sleep(LOCK_POLL_DELAY)
                waited += LOCK_POLL_DELAY
                cached = await r.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    data["_cached"] = True
                    break
                still_locked = await r.exists(lock_key)
                if not still_locked:
                    # Lock released but no cache (holder failed) — try ourselves
                    data = await fetch_json(
                        f"{settings.SCREENER_URL}/screener",
                        method="POST",
                        json_body=body,
                        timeout=15.0,
                    )
                    break

    except Exception:
        # Redis unavailable — fall through to direct call (no cache/lock)
        data = await fetch_json(
            f"{settings.SCREENER_URL}/screener",
            method="POST",
            json_body=body,
            timeout=15.0,
        )

    if "error" in data:
        return {"status": "unavailable", "results": [], "message": "Screener sedang tidak tersedia."}
    return {"status": "ok", **data}


@router.get("/terminal/screener/symbols")
async def screener_symbols():
    """List all symbols supported by the screener."""
    data = await fetch_json(f"{settings.SCREENER_URL}/symbols", timeout=8.0)
    if "error" in data:
        return {"symbols": []}
    return data
