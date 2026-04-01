"""
Trading Plan & Plan Features — Redis-backed.
Trading plan stored as JSON at: trading_plan:{user_id}
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from ...core.dependencies import get_current_user, get_current_user_info
import redis.asyncio as aioredis
import os
import json
from datetime import datetime, timezone

router = APIRouter(tags=["Trading Plan & Plan Features"])

REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
_redis = None

async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

# All 18 features with their plan access matrix
FEATURE_ACCESS_MAP = {
    "essential": [
        "technical", "signal", "alert", "session",
    ],
    "plus": [
        "technical", "signal", "alert", "session",
        "correlation", "fundamental", "calendar", "sentiment", "risk",
    ],
    "premium": [
        "technical", "signal", "alert", "session",
        "correlation", "fundamental", "calendar", "sentiment", "risk",
        "hybrid", "drawdown", "briefing", "psychology", "journal", "propfirm",
    ],
    "ultimate": [
        "technical", "signal", "alert", "session",
        "correlation", "fundamental", "calendar", "sentiment", "risk",
        "hybrid", "drawdown", "briefing", "psychology", "journal", "propfirm",
        "scanner", "backtesting", "mentor",
    ],
    "free": ["signal"],
}

ALL_FEATURES = [
    "technical", "signal", "alert", "session",
    "correlation", "fundamental", "calendar", "sentiment", "risk",
    "hybrid", "drawdown", "briefing", "psychology", "journal", "propfirm",
    "scanner", "backtesting", "mentor",
]

FEATURE_META = {
    "technical":   {"name": "Technical Analysis AI", "credit": 3,  "icon": "📈"},
    "signal":      {"name": "Signal System AI",       "credit": 3,  "icon": "⚡"},
    "alert":       {"name": "Smart Alert",            "credit": 1,  "icon": "🔔"},
    "session":     {"name": "Session Optimizer",      "credit": 1,  "icon": "⏰"},
    "correlation": {"name": "Correlation Tracker",    "credit": 3,  "icon": "🔗"},
    "fundamental": {"name": "Fundamental Analysis AI","credit": 5,  "icon": "🏦"},
    "calendar":    {"name": "Economic Calendar AI",   "credit": 4,  "icon": "📅"},
    "sentiment":   {"name": "Sentiment Market AI",    "credit": 5,  "icon": "📡"},
    "risk":        {"name": "Risk Manager AI",        "credit": 3,  "icon": "⚠️"},
    "hybrid":      {"name": "Hybrid System AI",       "credit": 8,  "icon": "🔮"},
    "drawdown":    {"name": "Drawdown Recovery",      "credit": 5,  "icon": "📉"},
    "briefing":    {"name": "AI Market Briefing",     "credit": 10, "icon": "📰"},
    "psychology":  {"name": "Psychology Coach AI",    "credit": 5,  "icon": "🧘"},
    "journal":     {"name": "AI Trade Journal",       "credit": 8,  "icon": "📓"},
    "propfirm":    {"name": "Prop Firm Assistant",    "credit": 8,  "icon": "🏦"},
    "scanner":     {"name": "Multi-Symbol Scanner",   "credit": 15, "icon": "🔍"},
    "backtesting": {"name": "AI Backtesting Engine",  "credit": 20, "icon": "📈"},
    "mentor":      {"name": "AI Mentor Mode",         "credit": 10, "icon": "👨‍🏫"},
}


class TradingPlanBody(BaseModel):
    title: Optional[str] = ""
    pairs: Optional[List[str]] = []
    strategy: Optional[str] = ""
    risk_per_trade: Optional[float] = 1.0
    max_daily_trades: Optional[int] = 5
    session_preference: Optional[str] = "London"
    notes: Optional[str] = ""
    goals: Optional[str] = ""
    rules: Optional[List[str]] = []


@router.get("/features")
async def get_plan_features(user_info: dict = Depends(get_current_user_info)):
    """Return which of the 18 AI features the current user can access."""
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]

    if is_admin:
        user_plan = "ultimate"
        allowed = ALL_FEATURES
    else:
        r = await _get_redis()
        user_plan = (await r.get(f"user:{user_id}:plan")) or "free"
        allowed = FEATURE_ACCESS_MAP.get(user_plan, FEATURE_ACCESS_MAP["free"])

    features = []
    for feature_id, meta in FEATURE_META.items():
        features.append({
            "id": feature_id,
            "name": meta["name"],
            "icon": meta["icon"],
            "credit_cost": 0 if is_admin else meta["credit"],
            "accessible": is_admin or (feature_id in allowed),
            "plan_required": next(
                (p for p, feats in FEATURE_ACCESS_MAP.items() if feature_id in feats),
                "essential"
            ),
        })

    return {
        "user_plan": user_plan,
        "is_admin": is_admin,
        "total_features": len(FEATURE_META),
        "accessible_count": len(features) if is_admin else len(allowed),
        "features": features,
    }


@router.get("/")
async def get_trading_plan(user_info: dict = Depends(get_current_user_info)):
    """Get the user's saved trading plan from Redis."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    raw = await r.get(f"trading_plan:{user_id}")
    if not raw:
        # Return empty plan template
        return {
            "exists": False,
            "plan": {
                "title": "",
                "pairs": [],
                "strategy": "",
                "risk_per_trade": 1.0,
                "max_daily_trades": 5,
                "session_preference": "London",
                "notes": "",
                "goals": "",
                "rules": [],
                "created_at": None,
                "updated_at": None,
            }
        }
    plan = json.loads(raw)
    return {"exists": True, "plan": plan}


@router.post("/")
async def create_trading_plan(
    body: TradingPlanBody,
    user_info: dict = Depends(get_current_user_info),
):
    """Create or replace the user's trading plan."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    now = datetime.now(timezone.utc).isoformat()

    # Check if already exists to preserve created_at
    raw = await r.get(f"trading_plan:{user_id}")
    created_at = now
    if raw:
        existing = json.loads(raw)
        created_at = existing.get("created_at", now)

    plan = {
        "user_id": user_id,
        "title": body.title,
        "pairs": body.pairs,
        "strategy": body.strategy,
        "risk_per_trade": body.risk_per_trade,
        "max_daily_trades": body.max_daily_trades,
        "session_preference": body.session_preference,
        "notes": body.notes,
        "goals": body.goals,
        "rules": body.rules,
        "created_at": created_at,
        "updated_at": now,
    }

    await r.set(f"trading_plan:{user_id}", json.dumps(plan))
    return {"message": "Trading plan saved", "plan": plan}


@router.put("/")
async def update_trading_plan(
    body: TradingPlanBody,
    user_info: dict = Depends(get_current_user_info),
):
    """Update the user's trading plan (partial update)."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    now = datetime.now(timezone.utc).isoformat()

    raw = await r.get(f"trading_plan:{user_id}")
    if not raw:
        raise HTTPException(status_code=404, detail="Belum ada trading plan. Buat dulu dengan POST.")
    plan = json.loads(raw)

    # Only update non-None / non-empty fields
    if body.title:            plan["title"] = body.title
    if body.pairs:            plan["pairs"] = body.pairs
    if body.strategy:         plan["strategy"] = body.strategy
    if body.risk_per_trade:   plan["risk_per_trade"] = body.risk_per_trade
    if body.max_daily_trades: plan["max_daily_trades"] = body.max_daily_trades
    if body.session_preference: plan["session_preference"] = body.session_preference
    if body.notes:            plan["notes"] = body.notes
    if body.goals:            plan["goals"] = body.goals
    if body.rules:            plan["rules"] = body.rules
    plan["updated_at"] = now

    await r.set(f"trading_plan:{user_id}", json.dumps(plan))
    return {"message": "Trading plan updated", "plan": plan}


@router.post("/ai-generate")
async def generate_ai_plan(user_info: dict = Depends(get_current_user_info)):
    """AI-generate a trading plan — Ultimate plan only."""
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]
    r = await _get_redis()
    user_plan = (await r.get(f"user:{user_id}:plan")) or "free"
    if not is_admin and user_plan != "ultimate":
        raise HTTPException(status_code=403, detail="Fitur ini hanya untuk plan Ultimate.")
    return {"message": "AI generated trading plan — connect strategy-core for full AI generation"}
