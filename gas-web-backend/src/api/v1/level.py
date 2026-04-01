from fastapi import APIRouter, Depends, HTTPException
from ...core.dependencies import get_current_user, get_current_user_info
import redis.asyncio as aioredis
import os

router = APIRouter(tags=["Level Progression"])

REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
_redis = None

async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

LEVEL_DEFINITIONS = [
    {"level": 1,  "xp_required": 0,    "reward": "Akses terminal dasar"},
    {"level": 2,  "xp_required": 100,  "reward": "+10 bonus credits"},
    {"level": 3,  "xp_required": 300,  "reward": "Custom avatar border"},
    {"level": 4,  "xp_required": 600,  "reward": "+25 bonus credits"},
    {"level": 5,  "xp_required": 1000, "reward": "Priority processing access"},
    {"level": 6,  "xp_required": 1500, "reward": "+50 bonus credits"},
    {"level": 7,  "xp_required": 2200, "reward": "Forum VIP early access"},
    {"level": 8,  "xp_required": 3000, "reward": "+100 bonus credits"},
    {"level": 9,  "xp_required": 4000, "reward": "Custom signal profile page"},
    {"level": 10, "xp_required": 5500, "reward": "GAS Legend — 20% off lifetime + exclusive badge"},
]

XP_REWARDS = {
    "technical_analysis": 10,
    "signal_generated":   15,
    "journal_entry":      20,
    "psychology_check":   10,
    "daily_login":        5,
    "briefing_read":      8,
    "hybrid_analysis":    25,
    "backtesting_run":    50,
    "mentor_session":     30,
    "trade_logged":       20,
}

PLAN_MULTIPLIERS = {"essential": 1.0, "plus": 1.5, "premium": 2.0, "ultimate": 3.0}


def _compute_level(xp: int) -> dict:
    current_level = 1
    for ld in LEVEL_DEFINITIONS:
        if xp >= ld["xp_required"]:
            current_level = ld["level"]
        else:
            break
    current_level = min(current_level, 10)
    prev_xp = LEVEL_DEFINITIONS[current_level - 1]["xp_required"]
    next_xp = LEVEL_DEFINITIONS[min(current_level, 9)]["xp_required"] if current_level < 10 else xp
    progress_pct = int(((xp - prev_xp) / max(1, next_xp - prev_xp)) * 100) if current_level < 10 else 100
    return {
        "level": current_level,
        "xp": xp,
        "xp_to_next": max(0, next_xp - xp),
        "progress_pct": min(100, progress_pct),
        "current_reward": LEVEL_DEFINITIONS[current_level - 1]["reward"],
        "next_reward": LEVEL_DEFINITIONS[current_level]["reward"] if current_level < 10 else "Max Level!",
    }


@router.get("/level")
async def get_user_level(user_info: dict = Depends(get_current_user_info)):
    """Get user's current level, XP, and progression info from Redis."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    xp = int(await r.get(f"user:{user_id}:xp") or 0)
    user_plan = (await r.get(f"user:{user_id}:plan")) or "essential"

    level_data = _compute_level(xp)
    multiplier = PLAN_MULTIPLIERS.get(user_plan, 1.0)
    plan_features = {
        "free": ["technical", "signal"],
        "essential": ["technical", "signal", "alert", "session"],
        "plus": ["technical", "signal", "alert", "session", "correlation", "fundamental", "calendar", "sentiment", "risk"],
        "premium": ["technical", "signal", "alert", "session", "correlation", "fundamental", "calendar", "sentiment", "risk", "hybrid", "drawdown", "briefing", "psychology", "journal", "propfirm"],
        "ultimate": ["technical", "signal", "alert", "session", "correlation", "fundamental", "calendar", "sentiment", "risk", "hybrid", "drawdown", "briefing", "psychology", "journal", "propfirm", "scanner", "backtesting", "mentor"],
    }

    return {
        **level_data,
        "levels": LEVEL_DEFINITIONS,
        "xp_rewards": {k: int(v * multiplier) for k, v in XP_REWARDS.items()},
        "plan_multipliers": PLAN_MULTIPLIERS,
        "xp_multiplier": multiplier,
        "user_plan": user_plan,
        "unlocked_features": plan_features.get(user_plan, plan_features["essential"]),
    }


@router.post("/level/add-xp")
async def add_xp(action: str = "daily_login", user_info: dict = Depends(get_current_user_info)):
    """Award XP for a completed action."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    user_plan = (await r.get(f"user:{user_id}:plan")) or "essential"
    multiplier = PLAN_MULTIPLIERS.get(user_plan, 1.0)
    base_xp = XP_REWARDS.get(action, 5)
    awarded = int(base_xp * multiplier)

    new_xp = await r.incrby(f"user:{user_id}:xp", awarded)
    level_data = _compute_level(int(new_xp))
    return {
        "action": action,
        "xp_awarded": awarded,
        "base_xp": base_xp,
        "multiplier": multiplier,
        **level_data,
    }
