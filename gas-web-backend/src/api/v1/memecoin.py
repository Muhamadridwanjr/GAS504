"""
GAS Memecoin Signal — Web Backend credit gate.
Plan: premium+ (premium, ultimate, ultra)
Credit cost: 5cr per AI signal analysis
Trending feed: FREE (no credits, just plan check)
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import httpx, json, os
import redis.asyncio as aioredis

from ...core.dependencies import get_current_user_info
from .billing import deduct_credits, get_user_credits

router = APIRouter(tags=["Memecoin Signal AI"])

MEMECOIN_SERVICE_URL = os.getenv("MEMECOIN_SERVICE_URL", "http://gas-memecoin-service:9614")
REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
CREDIT_AI_SIGNAL = 5
ALLOWED_PLANS = {"premium", "ultimate", "ultra"}

_redis = None
async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

async def _get_user_plan(user_id: str) -> str:
    try:
        r = await _get_redis()
        return await r.get(f"user:{user_id}:plan") or "essential"
    except Exception:
        return "essential"

async def _call_memecoin(endpoint: str, method="GET", body=None, params=None) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{MEMECOIN_SERVICE_URL}{endpoint}"
        try:
            resp = await client.post(url, json=body) if method == "POST" else await client.get(url, params=params)
            if resp.status_code == 200:
                return resp.json()
            raise HTTPException(status_code=resp.status_code, detail=resp.text[:200])
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=503, detail=str(e))


@router.post("/memecoin/signal")
async def memecoin_signal(
    body: dict,
    user_info: dict = Depends(get_current_user_info),
):
    """AI signal analysis — 5cr, requires Premium+ plan."""
    user_id  = user_info["user_id"]
    is_admin = user_info.get("is_admin", False)

    if not is_admin:
        plan = await _get_user_plan(user_id)
        if plan not in ALLOWED_PLANS:
            raise HTTPException(status_code=403,
                detail=f"Memecoin AI Signal membutuhkan plan Premium atau lebih tinggi. Plan kamu: {plan}.")

    # Check cache first
    token_address = body.get("token_address", "")
    try:
        r = await _get_redis()
        cache_key = f"gas:meme:signal:{token_address}"
        cached = await r.get(cache_key)
        if cached:
            data = json.loads(cached)
            data["from_cache"] = True
            data["credits_used"] = 0
            data["credits_remaining"] = await get_user_credits(user_id)
            return data
    except Exception:
        pass

    if not is_admin:
        success, remaining = await deduct_credits(user_id, CREDIT_AI_SIGNAL, is_admin=False)
        if not success:
            raise HTTPException(status_code=402,
                detail=f"Kredit tidak cukup. Butuh {CREDIT_AI_SIGNAL} cr. Tersisa {remaining} cr.")
    else:
        remaining = await get_user_credits(user_id)

    data = await _call_memecoin("/memecoin/signal", method="POST", body=body)
    data["credits_used"] = 0 if is_admin else CREDIT_AI_SIGNAL
    data["credits_remaining"] = remaining
    data["from_cache"] = False
    return data


@router.get("/memecoin/credits-info")
async def memecoin_credits_info(user_info: dict = Depends(get_current_user_info)):
    user_id  = user_info["user_id"]
    is_admin = user_info.get("is_admin", False)
    plan     = "admin" if is_admin else await _get_user_plan(user_id)
    credits  = await get_user_credits(user_id)
    return {
        "has_access":   is_admin or plan in ALLOWED_PLANS,
        "plan":         plan,
        "credits_balance": credits,
        "credit_costs": {"ai_signal": CREDIT_AI_SIGNAL, "trending_feed": 0},
        "plan_required": "Premium+",
        "is_admin":     is_admin,
    }
