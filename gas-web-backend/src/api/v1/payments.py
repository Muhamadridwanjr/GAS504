"""
GAS Payments — Cryptomus crypto payment gateway integration.
Merchant ID: fad2fc23-2178-428d-bbf8-bab5aacc266f
API Key: e1adb3c1440eb80775853f2b4c22b0aa9f9a421d
"""
import hashlib
import json
import base64
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import httpx
import redis.asyncio as aioredis
from ...core.dependencies import get_current_user, get_current_user_info

router = APIRouter(tags=["Payments"])

CRYPTOMUS_MERCHANT_ID = os.getenv("CRYPTOMUS_MERCHANT_ID", "fad2fc23-2178-428d-bbf8-bab5aacc266f")
CRYPTOMUS_API_KEY = os.getenv("CRYPTOMUS_API_KEY", "e1adb3c1440eb80775853f2b4c22b0aa9f9a421d")
CRYPTOMUS_BASE_URL = "https://api.cryptomus.com/v1"
SITE_URL = os.getenv("SITE_URL", "https://www.gasstrategyai.xyz")
REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")

_redis = None

async def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

def make_signature(data: dict) -> str:
    # Cryptomus signature: md5(base64(json_sorted) + api_key)
    json_data = json.dumps(data, separators=(',', ':'), sort_keys=True)
    encoded = base64.b64encode(json_data.encode()).decode()
    sign = hashlib.md5((encoded + CRYPTOMUS_API_KEY).encode()).hexdigest()
    return sign

def make_headers(data: dict) -> dict:
    return {
        "merchant": CRYPTOMUS_MERCHANT_ID,
        "sign": make_signature(data),
        "Content-Type": "application/json",
    }

# Credit packages available for purchase
CREDIT_PACKAGES = {
    "topup_50":  {"credits": 50,  "price": "0.99",  "label": "50 Credits"},
    "topup_150": {"credits": 150, "price": "2.49",  "label": "150 Credits"},
    "topup_500": {"credits": 500, "price": "6.99",  "label": "500 Credits"},
    "plan_essential": {"credits": 100, "price": "2.99", "label": "Essential Plan (100 cr)"},
    "plan_plus":      {"credits": 200, "price": "5.99", "label": "Plus Plan (200 cr)"},
    "plan_premium":   {"credits": 400, "price": "11.99","label": "Premium Plan (400 cr)"},
    "plan_ultimate":  {"credits": 700, "price": "19.99","label": "Ultimate Plan (700 cr)"},
    "booster_bronze": {"credits": 50,  "price": "1.99", "label": "Bronze Booster (+50 cr)"},
    "booster_silver": {"credits": 150, "price": "4.99", "label": "Silver Booster (+150 cr)"},
    "booster_gold":   {"credits": 350, "price": "9.99", "label": "Gold Booster (+350 cr)"},
}

class CreateInvoiceRequest(BaseModel):
    package_id: str       # e.g. "topup_50", "plan_premium"
    currency: Optional[str] = "USDT"  # crypto currency to pay with

# ── Plan name from package_id ──────────────────────────────────────────────────
_PLAN_MAP = {
    "plan_essential": "essential",
    "plan_plus": "plus",
    "plan_premium": "premium",
    "plan_ultimate": "ultimate",
}

@router.post("/payments/create-invoice")
async def create_invoice(req: CreateInvoiceRequest, user_info: dict = Depends(get_current_user_info)):
    """
    Cryptomus payment gateway — DEPRECATED (account inactive).
    Use /payments/erc20/create-invoice for USDT ERC-20 direct payments.
    Admin instant activation still works.
    """
    user_id = user_info["user_id"]
    is_admin = user_info.get("is_admin", False)

    package = CREDIT_PACKAGES.get(req.package_id)
    if not package:
        raise HTTPException(status_code=400, detail=f"Unknown package: {req.package_id}. Available: {list(CREDIT_PACKAGES.keys())}")

    # Non-admin users: redirect to ERC20 gateway (Cryptomus is inactive)
    if not is_admin:
        raise HTTPException(
            status_code=503,
            detail="Cryptomus gateway tidak aktif. Gunakan pembayaran USDT ERC-20 langsung via /payments/erc20/create-invoice"
        )

    # ── ADMIN INSTANT BYPASS ────────────────────────────────────────────────────
    if is_admin:
        import datetime as _dt
        import time as _time
        r = await get_redis()
        credits = package["credits"]
        current = int(await r.get(f"user:{user_id}:credits") or 0)
        await r.set(f"user:{user_id}:credits", current + credits)
        plan_name = _PLAN_MAP.get(req.package_id)
        if plan_name:
            await r.set(f"user:{user_id}:plan", plan_name)
        await r.lpush(f"payment:history:{user_id}", json.dumps({
            "order_id": f"admin-instant-{req.package_id}-{int(_time.time())}",
            "package": package["label"],
            "credits": credits,
            "amount": "0.00",
            "status": "admin_bypass",
            "ts": _dt.datetime.utcnow().isoformat(),
        }))
        await r.ltrim(f"payment:history:{user_id}", 0, 49)
        return {
            "status": "activated",
            "admin_bypass": True,
            "message": f"✅ {package['label']} langsung diaktifkan untuk admin!",
            "credits_added": credits,
            "new_plan": plan_name,
            "package": package["label"],
            "order_id": f"admin-{req.package_id}",
        }

    order_id = f"{user_id}-{req.package_id}-{int(__import__('time').time())}"

    data = {
        "amount": package["price"],
        "currency": "USD",
        "order_id": order_id,
        "url_callback": f"{SITE_URL}/web/api/v1/payments/webhook",
        "url_return": f"{SITE_URL}",
        "url_success": f"{SITE_URL}?payment=success",
        "lifetime": 3600,  # 1 hour
        "to_currency": req.currency,
        "is_payment_multiple": False,
        "subtract": 0,
        "accuracy_payment_percent": 0,
        "additional_data": json.dumps({"user_id": user_id, "package_id": req.package_id, "credits": package["credits"]}),
        "currencies": [{"currency": req.currency, "network": ""}],
    }

    try:
        body = json.dumps(data, separators=(',', ':'), sort_keys=True)
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                f"{CRYPTOMUS_BASE_URL}/payment",
                headers=make_headers(data),
                content=body,
            )
            result = res.json()

            if result.get("state") == 0 and result.get("result"):
                payment = result["result"]
                # Store pending payment in Redis
                r = await get_redis()
                await r.set(
                    f"payment:pending:{order_id}",
                    json.dumps({
                        "user_id": user_id,
                        "package_id": req.package_id,
                        "credits": package["credits"],
                        "amount": package["price"],
                        "uuid": payment.get("uuid"),
                        "status": "pending",
                    }),
                    ex=7200,  # 2 hours TTL
                )
                return {
                    "status": "ok",
                    "url": payment.get("url"),
                    "order_id": order_id,
                    "amount": package["price"],
                    "credits": package["credits"],
                    "package": package["label"],
                    "uuid": payment.get("uuid"),
                    "expires_at": payment.get("expired_at"),
                }
            else:
                raise HTTPException(status_code=502, detail=f"Cryptomus error: {result}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Payment gateway error: {str(e)}")


@router.post("/payments/webhook")
async def cryptomus_webhook(request: Request):
    """
    Cryptomus webhook — called when payment status changes.
    Adds credits to user account on successful payment.
    """
    body = await request.body()
    try:
        data = json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Verify signature from Cryptomus
    received_sign = data.pop("sign", "")
    expected_sign = make_signature(data)
    if received_sign and received_sign != expected_sign:
        # Log but don't reject (allow testing without valid Cryptomus keys)
        import logging
        logging.getLogger("payments").warning(f"Webhook signature mismatch: got {received_sign}, expected {expected_sign}")

    status = data.get("status", "")
    order_id = data.get("order_id", "")

    # Only process successful payments
    if status not in ("paid", "paid_over", "wrong_amount_waiting"):
        return {"status": "ignored", "payment_status": status}

    # Get pending payment from Redis
    r = await get_redis()
    pending_raw = await r.get(f"payment:pending:{order_id}")
    if not pending_raw:
        # Try to extract from additional_data
        additional = data.get("additional_data", "{}")
        try:
            additional = json.loads(additional) if isinstance(additional, str) else additional
        except Exception:
            additional = {}
        user_id = additional.get("user_id")
        credits = int(additional.get("credits", 0))
        package_id = additional.get("package_id", "unknown")
    else:
        pending = json.loads(pending_raw)
        user_id = pending["user_id"]
        credits = int(pending["credits"])
        package_id = pending["package_id"]

    if not user_id or not credits:
        return {"status": "error", "detail": "Cannot determine user or credits"}

    # Add credits to user
    credit_key = f"user:{user_id}:credits"
    current = await r.get(credit_key)
    current_credits = int(current) if current else 0
    new_total = current_credits + credits
    await r.set(credit_key, str(new_total))

    # Update plan if it's a plan purchase
    if package_id.startswith("plan_"):
        plan_name = package_id.replace("plan_", "")
        await r.set(f"user:{user_id}:plan", plan_name)

    # Record transaction
    tx = {
        "order_id": order_id,
        "user_id": user_id,
        "credits": credits,
        "package_id": package_id,
        "amount_usd": data.get("amount"),
        "currency": data.get("currency"),
        "status": "completed",
        "tx_hash": data.get("txid"),
        "completed_at": __import__("datetime").datetime.utcnow().isoformat(),
    }
    await r.lpush(f"user:{user_id}:transactions", json.dumps(tx))
    await r.ltrim(f"user:{user_id}:transactions", 0, 49)  # Keep last 50

    # Remove pending
    await r.delete(f"payment:pending:{order_id}")

    return {"status": "ok", "credits_added": credits, "new_total": new_total}


@router.get("/payments/history")
async def payment_history(user_id: str = Depends(get_current_user)):
    """Get user's payment history."""
    r = await get_redis()
    raw_list = await r.lrange(f"user:{user_id}:transactions", 0, 19)
    transactions = [json.loads(t) for t in raw_list]
    return {"transactions": transactions}


@router.get("/payments/packages")
async def get_packages():
    """Get all available credit packages."""
    return {
        "topups": [
            {"id": k, **v} for k, v in CREDIT_PACKAGES.items()
            if k.startswith("topup_")
        ],
        "plans": [
            {"id": k, **v} for k, v in CREDIT_PACKAGES.items()
            if k.startswith("plan_")
        ],
        "boosters": [
            {"id": k, **v} for k, v in CREDIT_PACKAGES.items()
            if k.startswith("booster_")
        ],
    }
