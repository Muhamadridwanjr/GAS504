"""
GAS Billing — Real credit system using Redis.
Credits stored in Redis: user:{user_id}:credits
Admin users (role=admin) always get ultimate plan + unlimited credits.

Atomic credit pattern (reserve → confirm | release):
  reservation_id = await reserve_credits(user_id, cost)
  try:
      result = await do_work()
      await confirm_reservation(reservation_id)
  except:
      await release_credits(reservation_id)
      raise
"""
from fastapi import APIRouter, Depends, HTTPException
from ...core.dependencies import get_current_user, get_current_user_info
import redis.asyncio as aioredis
import os
import json
import time
import uuid as _uuid

router = APIRouter(tags=["Billing"])

REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
_redis = None

PLAN_DEFAULT_CREDITS = {
    "essential": 100,
    "plus": 200,
    "premium": 400,
    "ultimate": 700,
    "ultra": 1500,
    "free": 20,
}

ADMIN_UNLIMITED_CREDITS = 999999


async def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


async def _ensure_admin_redis(user_id: str):
    """Set admin user to ultimate plan + unlimited credits in Redis."""
    r = await get_redis()
    await r.set(f"user:{user_id}:plan", "ultimate")
    await r.set(f"user:{user_id}:credits", str(ADMIN_UNLIMITED_CREDITS))


async def get_user_credits(user_id: str, is_admin: bool = False) -> int:
    if is_admin:
        await _ensure_admin_redis(user_id)
        return ADMIN_UNLIMITED_CREDITS
    r = await get_redis()
    raw = await r.get(f"user:{user_id}:credits")
    if raw is None:
        await r.set(f"user:{user_id}:credits", "20")
        return 20
    return int(raw)


async def deduct_credits(user_id: str, amount: int, is_admin: bool = False) -> tuple[bool, int]:
    """Deduct credits. Admin users are never deducted. Returns (success, remaining)."""
    if is_admin:
        return True, ADMIN_UNLIMITED_CREDITS
    r = await get_redis()
    current = await get_user_credits(user_id)
    if current < amount:
        return False, current
    new_balance = current - amount
    await r.set(f"user:{user_id}:credits", str(new_balance))
    # Log usage
    await r.lpush(f"user:{user_id}:usage", json.dumps({"amount": amount, "remaining": new_balance}))
    await r.ltrim(f"user:{user_id}:usage", 0, 99)
    return True, new_balance


# ── Lua script: atomic check-and-deduct ───────────────────────────────────────
_LUA_RESERVE = """
local bal = tonumber(redis.call('GET', KEYS[1]))
if bal == nil then
    redis.call('SET', KEYS[1], '20')
    bal = 20
end
local cost = tonumber(ARGV[1])
if bal < cost then
    return -1
end
local ttl = tonumber(ARGV[3]) or 120
redis.call('DECRBY', KEYS[1], cost)
redis.call('SETEX', KEYS[2], ttl, ARGV[2])
return bal - cost
"""

# TTL per model tier: must exceed request timeout + 30s buffer to prevent credit leak.
# Timeout budget: basic/advanced/pro=60s → TTL 90s; ultra/gpt=120s → TTL 150s; agent=180s → TTL 210s
TIER_RESERVATION_TTL = {
    "basic":    90,
    "advanced": 90,
    "pro":      90,
    "ultra":    150,
    "gpt":      150,
    "agent":    210,
}

_LUA_RELEASE = """
local data = redis.call('GET', KEYS[1])
if data then
    local ok, info = pcall(cjson.decode, data)
    if ok and info and info.cost and info.user_id then
        redis.call('INCRBY', 'user:' .. info.user_id .. ':credits', info.cost)
    end
    redis.call('DEL', KEYS[1])
    return 1
end
return 0
"""


async def reserve_credits(
    user_id: str,
    cost: int,
    is_admin: bool = False,
    model_tier: str = "basic",
) -> str | None:
    """
    Atomically deduct `cost` credits and create a reservation key.
    TTL is dynamic per model tier (must exceed request timeout + 30s buffer).
    Returns reservation_id on success, None if insufficient credits.
    Admin always succeeds with a no-op reservation.
    """
    if is_admin:
        return "admin_noop"
    r = await get_redis()
    reservation_id = str(_uuid.uuid4())
    credit_key     = f"user:{user_id}:credits"
    reserve_key    = f"credit_reserve:{reservation_id}"
    payload        = json.dumps({"user_id": user_id, "cost": cost})
    ttl            = TIER_RESERVATION_TTL.get(model_tier, 120)
    result = await r.eval(_LUA_RESERVE, 2, credit_key, reserve_key, str(cost), payload, str(ttl))
    if result == -1:
        return None   # insufficient credits
    # Log reservation in usage list
    await r.lpush(f"user:{user_id}:usage", json.dumps({"action": "reserve", "cost": cost, "ts": time.time()}))
    await r.ltrim(f"user:{user_id}:usage", 0, 99)
    return reservation_id


async def confirm_reservation(reservation_id: str):
    """Confirm the credit deduction — just deletes the reservation key."""
    if reservation_id == "admin_noop":
        return
    r = await get_redis()
    await r.delete(f"credit_reserve:{reservation_id}")


async def release_credits(reservation_id: str):
    """
    Rollback — restore credits to the user if the operation failed.
    Safe to call even if the reservation has already expired (TTL 120s).
    """
    if reservation_id == "admin_noop":
        return
    r = await get_redis()
    await r.eval(_LUA_RELEASE, 1, f"credit_reserve:{reservation_id}")


async def get_user_xp(user_id: str) -> int:
    r = await get_redis()
    raw = await r.get(f"user:{user_id}:xp")
    return int(raw) if raw else 0


async def get_user_level(xp: int) -> int:
    """Calculate level from XP. Level 1-20."""
    XP_TABLE = [0, 100, 250, 500, 850, 1300, 1900, 2700, 3700, 5000,
                6700, 8700, 11000, 13700, 16800, 20300, 24200, 28500, 33200, 38300]
    level = 1
    for i, threshold in enumerate(XP_TABLE):
        if xp >= threshold:
            level = i + 1
    return min(level, 20)


@router.get("/billing/status")
async def get_billing_status(user_info: dict = Depends(get_current_user_info)):
    """Get real credit balance, plan, level, XP from Redis."""
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]

    r = await get_redis()

    # Admin: auto-set ultimate plan + unlimited credits
    if is_admin:
        await _ensure_admin_redis(user_id)

    credits = await get_user_credits(user_id, is_admin)
    xp = await get_user_xp(user_id)
    level = await get_user_level(xp)
    booster = (await r.get(f"user:{user_id}:booster")) or ""
    booster_expires_ts = int((await r.get(f"user:{user_id}:booster_expires_at")) or 0)

    if is_admin:
        plan = "ultimate"
    else:
        plan = (await r.get(f"user:{user_id}:plan")) or "free"
        # Auto-expire trial
        if plan == "trial":
            trial_exp = int((await r.get(f"user:{user_id}:trial_expires_at")) or 0)
            if trial_exp and time.time() > trial_exp:
                await r.set(f"user:{user_id}:plan", "free")
                plan = "free"

    plan_expires_dt = (await r.get(f"user:{user_id}:plan_expires_dt")) or ""
    plan_expires_ts = int((await r.get(f"user:{user_id}:plan_expires_at")) or 0)
    trial_expires_dt = (await r.get(f"user:{user_id}:trial_expires_dt")) or ""
    trial_expires_ts = int((await r.get(f"user:{user_id}:trial_expires_at")) or 0)

    # Next level XP threshold
    XP_TABLE = [0, 100, 250, 500, 850, 1300, 1900, 2700, 3700, 5000,
                6700, 8700, 11000, 13700, 16800, 20300, 24200, 28500, 33200, 38300]
    xp_for_next = XP_TABLE[level] if level < 20 else XP_TABLE[19]
    xp_current_level = XP_TABLE[level - 1] if level > 1 else 0
    xp_progress = xp - xp_current_level
    xp_needed = xp_for_next - xp_current_level

    return {
        "credits": credits,
        "plan": plan,
        "tier": plan,
        "level": level,
        "level_score": xp,
        "xp": xp,
        "xp_progress": xp_progress,
        "xp_needed": xp_needed,
        "xp_to_next": max(0, xp_for_next - xp),
        "daily_usage": 0,
        "daily_limit": 999 if not is_admin else 999999,
        "quota": credits,
        "boost": 0,
        "is_admin": is_admin,
        "plan_expires_dt": plan_expires_dt,
        "plan_expires_ts": plan_expires_ts,
        "trial_expires_dt": trial_expires_dt,
        "trial_expires_ts": trial_expires_ts,
        "is_trial": plan == "trial",
        "booster": booster,
        "booster_expires_ts": booster_expires_ts,
    }


@router.get("/billing/credits")
async def get_credits(user_info: dict = Depends(get_current_user_info)):
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]
    credits = await get_user_credits(user_id, is_admin)
    return {"credits": credits, "user_id": user_id, "is_admin": is_admin}


@router.post("/billing/add-credits")
async def add_credits_internal(amount: int, user_info: dict = Depends(get_current_user_info)):
    """Add credits to user (called internally after payment confirmation)."""
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]
    r = await get_redis()
    if is_admin:
        return {"credits": ADMIN_UNLIMITED_CREDITS, "added": amount, "note": "Admin unlimited"}
    current = await get_user_credits(user_id)
    new_balance = current + amount
    await r.set(f"user:{user_id}:credits", str(new_balance))
    return {"credits": new_balance, "added": amount}


@router.get("/billing/history")
async def get_billing_history(user_id: str = Depends(get_current_user)):
    r = await get_redis()
    raw = await r.lrange(f"user:{user_id}:transactions", 0, 19)
    return [json.loads(t) for t in raw]


@router.get("/billing/usage")
async def get_billing_usage(user_id: str = Depends(get_current_user)):
    r = await get_redis()
    raw = await r.lrange(f"user:{user_id}:usage", 0, 49)
    return [json.loads(t) for t in raw]
