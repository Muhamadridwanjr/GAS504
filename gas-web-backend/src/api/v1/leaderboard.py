"""
Leaderboard — real data from Redis sorted sets.
leaderboard:pnl    → sorted by cumulative PnL (zadd + zincrby from journal)
leaderboard:trades → sorted by trade count
leaderboard:xp     → sorted by XP (existing user:{id}:xp keys)

Rankings are computed on-demand from Redis, cached for 60s.
"""
from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user_info
import redis.asyncio as aioredis
import os
import json
import math

router = APIRouter(tags=["Leaderboard"])

REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
_redis = None

async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

BADGE_THRESHOLDS = [
    (5500, "Legendary"), (3000, "Master"), (2200, "Diamond"),
    (1500, "Platinum"), (1000, "Gold"), (300, "Silver"), (0, "Bronze"),
]

def _xp_to_badge(xp: int) -> str:
    for threshold, badge in BADGE_THRESHOLDS:
        if xp >= threshold:
            return badge
    return "Bronze"

def _xp_to_level(xp: int) -> int:
    for threshold, lvl in [(5500,10),(4000,9),(3000,8),(2200,7),(1500,6),(1000,5),(600,4),(300,3),(100,2)]:
        if xp >= threshold:
            return lvl
    return 1


@router.get("/leaderboard")
async def get_leaderboard(
    period: str = "all",       # all | month | week (week/month approximate by trade recency)
    limit: int = 10,
    user_info: dict = Depends(get_current_user_info),
):
    """
    Return top traders by PnL from journal data.
    Also returns current user's rank.
    """
    r = await _get_redis()
    current_user_id = user_info["user_id"]

    # Try cached result (60s TTL)
    cache_key = f"leaderboard:cache:{period}:{limit}"
    cached = await r.get(cache_key)
    if cached:
        result = json.loads(cached)
        # Inject current user rank dynamically
        result["my_rank"] = await _get_my_rank(r, current_user_id, period)
        return result

    # Build leaderboard from Redis sorted set
    board_key = "leaderboard:pnl"
    members = await r.zrevrange(board_key, 0, limit - 1, withscores=True)

    traders = []
    for rank, (user_id, pnl_score) in enumerate(members, start=1):
        username = await r.get(f"user:{user_id}:username") or user_id[:8]
        xp       = int(await r.get(f"user:{user_id}:xp") or 0)
        trades   = int(await r.zscore("leaderboard:trades", user_id) or 0)
        level    = _xp_to_level(xp)
        badge    = _xp_to_badge(xp)

        # Compute stats from journal entries
        index_key = f"journal:{user_id}:index"
        entry_ids = await r.zrevrange(index_key, 0, -1)
        wins = 0
        for eid in entry_ids:
            pnl_raw = await r.hget(f"journal:{user_id}:{eid}", "pnl")
            try:
                if pnl_raw and float(pnl_raw) >= 0:
                    wins += 1
            except Exception:
                pass
        win_rate = round(wins / max(trades, 1) * 100, 1)

        traders.append({
            "rank":    rank,
            "name":    username,
            "avatar":  username[:2].upper(),
            "pnl":     round(pnl_score, 2),
            "trades":  trades,
            "win_rate": win_rate,
            "badge":   badge,
            "level":   level,
            "xp":      xp,
        })

    # If leaderboard is empty, return empty (no fake data)
    result = {
        "leaderboard": traders,
        "total": len(traders),
        "period": period,
        "data_source": "real" if traders else "empty",
    }

    # Cache for 60s
    await r.set(cache_key, json.dumps(result), ex=60)

    result["my_rank"] = await _get_my_rank(r, current_user_id, period)
    return result


async def _get_my_rank(r, user_id: str, period: str) -> dict:
    """Get current user's rank and stats from leaderboard."""
    rank_pos = await r.zrevrank("leaderboard:pnl", user_id)
    pnl = await r.zscore("leaderboard:pnl", user_id)
    trades = int(await r.zscore("leaderboard:trades", user_id) or 0)
    xp = int(await r.get(f"user:{user_id}:xp") or 0)
    username = await r.get(f"user:{user_id}:username") or user_id[:8]
    total_members = await r.zcard("leaderboard:pnl")

    return {
        "rank":     (rank_pos + 1) if rank_pos is not None else total_members + 1,
        "name":     username,
        "pnl":      round(pnl or 0, 2),
        "trades":   trades,
        "xp":       xp,
        "badge":    _xp_to_badge(xp),
        "level":    _xp_to_level(xp),
        "total_users": total_members,
    }
