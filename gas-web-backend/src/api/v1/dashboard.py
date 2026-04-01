"""
Dashboard aggregator — fetches real data from Redis and internal APIs.
"""
from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user, get_current_user_info
import redis.asyncio as aioredis
import httpx
import os
import json
import asyncio

router = APIRouter(tags=["Dashboard"])

REDIS_URL      = os.getenv("REDIS_URL",           "redis://gas-redis:6379/0")
BILLING_URL    = os.getenv("BILLING_SERVICE_URL",  "http://gas-billing-service:8004")
SIGNAL_URL     = os.getenv("SIGNAL_SERVICE_URL",   "http://gas-signal-service:8106")
AUTH_URL       = os.getenv("AUTH_SERVICE_URL",     "http://gas-auth-service:8001")

_redis = None

async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


async def _safe_get(url: str, headers: dict = None, timeout: float = 4.0) -> dict:
    """HTTP GET with graceful fallback."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url, headers=headers or {})
            if r.status_code < 400:
                return r.json()
    except Exception:
        pass
    return {}


@router.get("/summary")
async def get_dashboard_summary(user_info: dict = Depends(get_current_user_info)):
    user_id = user_info["user_id"]
    r = await _get_redis()
    credits = int(await r.get(f"user:{user_id}:credits") or 0)
    xp      = int(await r.get(f"user:{user_id}:xp") or 0)
    plan    = await r.get(f"user:{user_id}:plan") or "free"
    return {
        "user_id": user_id,
        "is_admin": user_info["is_admin"],
        "credits": credits,
        "xp": xp,
        "plan": "ultimate" if user_info["is_admin"] else plan,
    }


@router.get("/full")
async def get_dashboard_full(user_info: dict = Depends(get_current_user_info)):
    """Aggregate real data from Redis and internal services."""
    user_id  = user_info["user_id"]
    is_admin = user_info["is_admin"]
    r = await _get_redis()

    # ── Redis reads (fast, local) ─────────────────────────────────────────
    async def _redis_user():
        credits = int(await r.get(f"user:{user_id}:credits") or (999999 if is_admin else 0))
        xp      = int(await r.get(f"user:{user_id}:xp") or 0)
        plan    = await r.get(f"user:{user_id}:plan") or ("ultimate" if is_admin else "free")
        return {"credits": credits, "xp": xp, "plan": plan, "is_admin": is_admin}

    async def _redis_journal_stats():
        index_key = f"journal:{user_id}:index"
        total = await r.zcard(index_key)
        # Get last 5 entries for quick summary
        entry_ids = await r.zrevrange(index_key, 0, 4)
        pnls = []
        for eid in entry_ids:
            data = await r.hgetall(f"journal:{user_id}:{eid}")
            if data.get("pnl"):
                try:
                    pnls.append(float(data["pnl"]))
                except Exception:
                    pass
        wins = sum(1 for p in pnls if p >= 0)
        total_pnl = sum(pnls)
        win_rate = (wins / len(pnls) * 100) if pnls else 0
        return {
            "total_trades": total,
            "winrate": round(win_rate, 1),
            "profit": round(total_pnl, 2),
            "recent_count": len(pnls),
        }

    async def _redis_tcg():
        xp    = int(await r.get(f"user:{user_id}:xp") or 0)
        cards = await r.llen(f"tcg:{user_id}:cards")
        equipped = await r.get(f"tcg:{user_id}:equipped") or ""
        level = 1
        for threshold, lvl in [(100,2),(300,3),(600,4),(1000,5),(1500,6),(2200,7),(3000,8),(4000,9),(5500,10)]:
            if xp >= threshold:
                level = lvl
        return {"level": level, "cards_count": cards, "equipped": equipped}

    async def _redis_notifications():
        raw_list = await r.lrange(f"notifications:{user_id}", 0, 4)
        system   = await r.lrange("notifications:system", 0, 2)
        items = []
        for raw in raw_list + system:
            try:
                items.append(json.loads(raw))
            except Exception:
                pass
        return items

    async def _redis_analysis_history():
        raw_list = await r.lrange(f"analysis_history:{user_id}", 0, 4)
        entries = []
        for raw in raw_list:
            try:
                entries.append(json.loads(raw))
            except Exception:
                pass
        return entries

    # ── Run all concurrently ──────────────────────────────────────────────
    (
        user_data, journal_data, tcg_data, notif_data, history_data,
    ) = await asyncio.gather(
        _redis_user(),
        _redis_journal_stats(),
        _redis_tcg(),
        _redis_notifications(),
        _redis_analysis_history(),
        return_exceptions=True,
    )

    def _safe(v, default):
        return v if not isinstance(v, Exception) else default

    return {
        "user":             _safe(user_data, {"credits": 0, "xp": 0, "plan": "free"}),
        "journal":          _safe(journal_data, {"total_trades": 0, "winrate": 0, "profit": 0}),
        "tcg":              _safe(tcg_data, {"level": 1, "cards_count": 0, "equipped": ""}),
        "notifications":    _safe(notif_data, []),
        "analysis_history": _safe(history_data, []),
    }
