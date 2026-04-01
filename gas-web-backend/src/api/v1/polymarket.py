"""
GAS Polymarket Prediction — Web Backend
Credit deduction + plan gate for Polymarket predict calls.
Plan required: ultra (Ultra Ultimate plan)
Credit cost: 8 cr per full predict (4 agents), 3 cr per signal-only
Admin: bypass credit + plan check.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import httpx, json, os
from datetime import datetime, timezone
import redis.asyncio as aioredis

from ...core.dependencies import get_current_user_info
from .billing import deduct_credits, get_user_credits

router = APIRouter(tags=["Polymarket Signal AI"])

POLYMARKET_SERVICE_URL = os.getenv("POLYMARKET_SERVICE_URL", "http://gas-polymarket-service:9613")
REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
STRATEGY_CORE_URL = os.getenv("STRATEGY_CORE_URL", "http://gas-strategy-core:7003")

CREDIT_PREDICT_FULL   = 8   # 4-model agent consensus predict
CREDIT_PREDICT_SIGNAL = 3   # single GAS signal only

# Plans that have access (ultra = Ultra Ultimate, ultimate included too)
ALLOWED_PLANS = {"ultra", "ultimate"}

_redis = None
async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

async def _get_user_plan(user_id: str) -> str:
    try:
        r = await _get_redis()
        plan = await r.get(f"user:{user_id}:plan")
        return plan or "essential"
    except Exception:
        return "essential"

async def _call_polymarket(endpoint: str, method: str = "GET", body: dict = None, params: dict = None) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{POLYMARKET_SERVICE_URL}{endpoint}"
        try:
            if method == "POST":
                resp = await client.post(url, json=body)
            else:
                resp = await client.get(url, params=params)
            if resp.status_code == 200:
                return resp.json()
            raise HTTPException(status_code=resp.status_code, detail=f"Polymarket service error: {resp.text[:200]}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Polymarket service unavailable: {str(e)}")


class PredictRequest(BaseModel):
    event_id: str
    question: str
    category: str
    yes_price: float
    no_price: float
    pair: Optional[str] = None
    models: Optional[List[str]] = ["claude", "gpt", "gemini", "grok"]
    signal_only: bool = False   # True = 3cr single signal, False = 8cr full 4-agent


@router.post("/polymarket/predict")
async def polymarket_predict(
    body: PredictRequest,
    user_info: dict = Depends(get_current_user_info),
):
    """
    Run Polymarket prediction with credit deduction.
    - Full predict (4 agents): 8 cr — plan: ultra/ultimate
    - Signal only: 3 cr — plan: ultimate minimum
    - Admin: free, no plan check
    """
    user_id  = user_info["user_id"]
    is_admin = user_info.get("is_admin", False)

    # ── Plan gate ──────────────────────────────────────────────────────────
    if not is_admin:
        plan = await _get_user_plan(user_id)
        if plan not in ALLOWED_PLANS:
            raise HTTPException(
                status_code=403,
                detail=f"Polymarket Signal AI membutuhkan plan Ultra Ultimate. Plan kamu: {plan.capitalize()}. "
                       f"Upgrade di halaman Pricing."
            )

    # ── Credit check ───────────────────────────────────────────────────────
    cost = CREDIT_PREDICT_SIGNAL if body.signal_only else CREDIT_PREDICT_FULL

    # Check cache first — if already cached, no credit deducted
    try:
        r = await _get_redis()
        cache_key = f"gas:poly:predict2:{body.event_id}"
        cached = await r.get(cache_key)
        if cached:
            data = json.loads(cached)
            data["from_cache"] = True
            data["credits_used"] = 0
            data["credits_remaining"] = await get_user_credits(user_id)
            return data
    except Exception:
        pass

    # Deduct credits
    if not is_admin:
        success, remaining = await deduct_credits(user_id, cost, is_admin=False)
        if not success:
            raise HTTPException(
                status_code=402,
                detail=f"Kredit tidak cukup. Butuh {cost} cr untuk Polymarket Predict. "
                       f"Tersisa {remaining} cr. Top-up di Pricing."
            )
    else:
        # Admin: get balance for display only
        remaining = await get_user_credits(user_id)

    # ── Call polymarket-service ────────────────────────────────────────────
    payload = body.model_dump()
    if body.signal_only:
        payload["models"] = ["claude"]   # single model for signal-only

    data = await _call_polymarket("/polymarket/predict", method="POST", body=payload)

    data["credits_used"]      = 0 if is_admin else cost
    data["credits_remaining"] = remaining
    data["from_cache"]        = False
    data["plan_required"]     = "Ultra Ultimate"

    return data


@router.get("/polymarket/credits-info")
async def polymarket_credits_info(
    user_info: dict = Depends(get_current_user_info),
):
    """Return credit costs and plan info for Polymarket feature."""
    user_id  = user_info["user_id"]
    is_admin = user_info.get("is_admin", False)
    plan     = "admin" if is_admin else await _get_user_plan(user_id)
    credits  = await get_user_credits(user_id)
    has_access = is_admin or plan in ALLOWED_PLANS

    return {
        "has_access": has_access,
        "plan": plan,
        "credits_balance": credits,
        "credit_costs": {
            "full_predict_4agents": CREDIT_PREDICT_FULL,
            "signal_only":          CREDIT_PREDICT_SIGNAL,
        },
        "is_admin": is_admin,
        "plan_required": "Ultra Ultimate",
    }
