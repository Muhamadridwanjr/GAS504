"""
GAS Booster System API — Bronze / Silver / Gold Boosters + Level progression
From gasfiturmap.md: Booster & Leveling System
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ...core.dependencies import get_current_user, get_current_user_info

router = APIRouter(tags=["Booster & Level System"])

# Booster packs from gasfiturmap.md
BOOSTER_PACKS = [
    {
        "id": "bronze_7d",
        "name": "Bronze Booster",
        "emoji": "🥉",
        "duration_days": 7,
        "price_usd": 1.99,
        "bonus_credits": 50,
        "tier_upgrade": 1,
        "badge": "bronze",
        "description": "Naik 1 tier sementara selama 7 hari + 50 bonus credits",
    },
    {
        "id": "silver_14d",
        "name": "Silver Booster",
        "emoji": "🥈",
        "duration_days": 14,
        "price_usd": 4.99,
        "bonus_credits": 150,
        "tier_upgrade": 1,
        "badge": "silver",
        "description": "Naik 1 tier sementara selama 14 hari + 150 bonus credits",
    },
    {
        "id": "gold_30d",
        "name": "Gold Booster",
        "emoji": "🥇",
        "duration_days": 30,
        "price_usd": 9.99,
        "bonus_credits": 350,
        "tier_upgrade": 1,
        "badge": "gold",
        "description": "Naik 1 tier sementara selama 30 hari + 350 bonus credits",
    },
]

# Level definitions (Level 1-10)
LEVEL_DEFINITIONS = [
    {"level": 1,  "xp_required": 0,     "reward": "Akses terminal dasar",              "badge": "starter"},
    {"level": 2,  "xp_required": 100,   "reward": "+10 bonus credits",                 "badge": "trader"},
    {"level": 3,  "xp_required": 300,   "reward": "Custom avatar border",              "badge": "analyst"},
    {"level": 4,  "xp_required": 600,   "reward": "+25 bonus credits",                 "badge": "expert"},
    {"level": 5,  "xp_required": 1000,  "reward": "Priority processing access",        "badge": "pro"},
    {"level": 6,  "xp_required": 1500,  "reward": "+50 bonus credits",                 "badge": "elite"},
    {"level": 7,  "xp_required": 2200,  "reward": "Forum VIP early access",            "badge": "master"},
    {"level": 8,  "xp_required": 3000,  "reward": "+100 bonus credits",                "badge": "grandmaster"},
    {"level": 9,  "xp_required": 4000,  "reward": "Custom signal profile page",        "badge": "legend_candidate"},
    {"level": 10, "xp_required": 5500,  "reward": "GAS Legend — 20% off lifetime + exclusive badge", "badge": "gas_legend"},
]

# XP rewards per activity
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
    "prop_firm_pass":     500,
}


class PurchaseRequest(BaseModel):
    pack_id: str
    payment_method: Optional[str] = "stripe"


class AddXpRequest(BaseModel):
    activity: str
    plan: Optional[str] = "essential"


@router.get("/packs")
async def get_booster_packs(user_info: dict = Depends(get_current_user_info)):
    """Get all available booster packs with pricing."""
    return {
        "packs": BOOSTER_PACKS,
        "note": "Booster naik 1 tier sementara — unlock fitur & model AI lebih tinggi + bonus credits",
    }


@router.post("/purchase")
async def purchase_booster(req: PurchaseRequest, user_id: str = Depends(get_current_user)):
    """Purchase a booster pack. In production, integrates with payment gateway."""
    pack = next((p for p in BOOSTER_PACKS if p["id"] == req.pack_id), None)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Booster pack '{req.pack_id}' tidak ditemukan")

    return {
        "status": "success",
        "message": f"{pack['emoji']} {pack['name']} berhasil diaktifkan!",
        "pack": pack,
        "user_id": user_id,
        "bonus_credits_added": pack["bonus_credits"],
        "tier_upgraded": True,
        "duration_days": pack["duration_days"],
        "badge_unlocked": pack["badge"],
        "expires_at": None,  # Set by billing service in production
        "payment_method": req.payment_method,
        "note": "Profil badge sudah diupgrade dan terlihat publik di platform.",
    }


@router.get("/levels")
async def get_level_definitions(user_info: dict = Depends(get_current_user_info)):
    """Get all level definitions with XP requirements and rewards."""
    return {
        "levels": LEVEL_DEFINITIONS,
        "xp_activities": XP_REWARDS,
        "plan_multipliers": {
            "essential": 1.0,
            "plus":      1.5,
            "premium":   2.0,
            "ultimate":  3.0,
        },
        "max_level": 10,
        "legend_reward": "20% off lifetime subscription + exclusive GAS Legend badge",
    }


@router.get("/my-level")
async def get_my_level(user_info: dict = Depends(get_current_user_info)):
    """Get current user's level progress from Redis."""
    import redis.asyncio as aioredis, os
    user_id = user_info["user_id"]
    r = aioredis.from_url(os.getenv("REDIS_URL", "redis://gas-redis:6379/0"), decode_responses=True)
    raw_xp = await r.get(f"user:{user_id}:xp")
    current_xp = int(raw_xp) if raw_xp else 0

    # Calculate level from XP
    current_level = 1
    for i, lvl in enumerate(LEVEL_DEFINITIONS):
        if current_xp >= lvl["xp_required"]:
            current_level = i + 1

    # current_level is 1-based; index into 0-based LEVEL_DEFINITIONS is current_level-1
    # next level index is current_level (since list is 0-indexed)
    next_level = LEVEL_DEFINITIONS[current_level] if current_level < len(LEVEL_DEFINITIONS) else None
    prev_xp = LEVEL_DEFINITIONS[current_level - 1]["xp_required"]
    next_xp = next_level["xp_required"] if next_level else prev_xp + 1
    progress_pct = int(((current_xp - prev_xp) / max(1, next_xp - prev_xp)) * 100)

    await r.aclose()
    return {
        "user_id": user_id,
        "is_admin": user_info["is_admin"],
        "current_level": current_level,
        "current_xp": current_xp,
        "xp_to_next": max(0, next_xp - current_xp),
        "progress_pct": min(100, progress_pct),
        "current_badge": LEVEL_DEFINITIONS[current_level - 1]["badge"],
        "next_level_reward": next_level["reward"] if next_level else "Max level reached — GAS Legend!",
        "level_info": LEVEL_DEFINITIONS[current_level - 1],
        "active_booster": None,
    }


@router.post("/add-xp")
async def add_xp(req: AddXpRequest, user_info: dict = Depends(get_current_user_info)):
    """Award XP for a completed activity. Writes to Redis."""
    import redis.asyncio as aioredis, os
    user_id = user_info["user_id"]
    base_xp = XP_REWARDS.get(req.activity, 5)
    plan_multipliers = {"essential": 1.0, "plus": 1.5, "premium": 2.0, "ultimate": 3.0}
    multiplier = plan_multipliers.get(req.plan, 1.0)
    earned_xp = int(base_xp * multiplier)

    r = aioredis.from_url(os.getenv("REDIS_URL", "redis://gas-redis:6379/0"), decode_responses=True)
    current_raw = await r.get(f"user:{user_id}:xp")
    current_xp = int(current_raw) if current_raw else 0
    new_xp = current_xp + earned_xp
    await r.set(f"user:{user_id}:xp", str(new_xp))
    await r.aclose()

    return {
        "activity": req.activity,
        "base_xp": base_xp,
        "multiplier": multiplier,
        "earned_xp": earned_xp,
        "total_xp": new_xp,
        "user_id": user_id,
        "message": f"+{earned_xp} XP earned dari {req.activity}!",
    }


@router.get("/credit-topup")
async def get_credit_topup_options(user_info: dict = Depends(get_current_user_info)):
    """Get available credit top-up options."""
    return {
        "options": [
            {"id": "cr_50",  "credits": 50,  "price_usd": 0.99, "label": "Starter Pack",   "per_cr": "$0.020"},
            {"id": "cr_150", "credits": 150, "price_usd": 2.49, "label": "Value Pack",     "per_cr": "$0.017"},
            {"id": "cr_500", "credits": 500, "price_usd": 6.99, "label": "Power Pack",     "per_cr": "$0.014"},
        ],
        "note": "Credits tidak expired dan rollover ke bulan berikutnya (sesuai plan).",
    }
