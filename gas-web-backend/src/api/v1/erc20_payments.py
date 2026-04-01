"""
GAS ERC20 USDT Payment System
Wallet: 0xf8ef68F41B609B06210ebe7d045FA111F2034518
Payment verification via Etherscan API
"""
import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel

from ...core.dependencies import get_current_user, get_current_user_info

logger = logging.getLogger("gas.erc20")

router = APIRouter(tags=["ERC20 Payments"])

# ── Config ───────────────────────────────────────────────────────────────────
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "QQXE85JN3C1B6YIPBWRQNS5FK7GCMH2IKE")
ETHERSCAN_BASE    = "https://api.etherscan.io/v2/api"
ETHERSCAN_CHAIN   = "1"   # Ethereum mainnet
WALLET_ADDRESS    = os.getenv("ERC20_WALLET", "0xf8ef68F41B609B06210ebe7d045FA111F2034518")
USDT_CONTRACT     = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT ERC20
BANK_ACCOUNT      = os.getenv("BANK_ACCOUNT", "")  # Format: "BCA 1234567890 a.n. Nama"
USDT_DECIMALS     = 6   # USDT uses 6 decimal places
REDIS_URL         = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
SITE_URL          = os.getenv("SITE_URL", "https://www.gasstrategyai.xyz")
INVOICE_TTL_SEC   = 3600   # 1 hour
POLL_INTERVAL_SEC = 60     # Poll Etherscan every 60s

# ── Plan / package catalogue ─────────────────────────────────────────────────
PACKAGES = {
    # Plans
    "plan_essential": {
        "credits": 100, "price_usd": "2.99",  "label": "Essential Plan",   "plan": "essential"},
    "plan_plus": {
        "credits": 200, "price_usd": "5.99",  "label": "Plus Plan",        "plan": "plus"},
    "plan_premium": {
        "credits": 400, "price_usd": "11.99", "label": "Premium Plan",     "plan": "premium"},
    "plan_ultimate": {
        "credits": 700,  "price_usd": "19.99", "label": "Ultimate Plan",       "plan": "ultimate"},
    "plan_ultra": {
        "credits": 1500, "price_usd": "39.99", "label": "Ultra Ultimate Plan",  "plan": "ultra"},
    # Top-ups
    "topup_50":  {"credits": 50,  "price_usd": "0.99",  "label": "Top-up 50 Credits",  "plan": ""},
    "topup_150": {"credits": 150, "price_usd": "2.49",  "label": "Top-up 150 Credits", "plan": ""},
    "topup_500": {"credits": 500, "price_usd": "6.99",  "label": "Top-up 500 Credits", "plan": ""},
    # Boosters — credits + XP reward + badge TTL
    "booster_bronze": {"credits": 50,  "price_usd": "1.99", "label": "Bronze Booster", "plan": "", "xp": 200,  "badge_days": 7},
    "booster_silver": {"credits": 150, "price_usd": "4.99", "label": "Silver Booster", "plan": "", "xp": 500,  "badge_days": 14},
    "booster_gold":   {"credits": 350, "price_usd": "9.99", "label": "Gold Booster",   "plan": "", "xp": 1000, "badge_days": 30},
}

_redis_client: Optional[aioredis.Redis] = None


async def _get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


def _usdt_raw(amount_str: str) -> int:
    """Convert decimal USDT string to raw integer (6 decimals)."""
    val = float(amount_str)
    return int(round(val * 10 ** USDT_DECIMALS))


def _usdt_display(raw: int) -> str:
    """Convert raw integer to display string."""
    return f"{raw / 10 ** USDT_DECIMALS:.4f}"


def _unique_amount(base_price_str: str, order_suffix: str) -> str:
    """
    Add a micro-variation (0.0000–0.0099 USDT) based on order_suffix so each
    invoice has a distinct exact amount. Variation is < 1 cent.
    """
    base_raw = _usdt_raw(base_price_str)
    # Use last 2 hex chars of sha256(order_suffix) → 0..255 micro-units
    h = hashlib.sha256(order_suffix.encode()).hexdigest()
    micro = int(h[-2:], 16) % 100  # 0..99 micro-USDT units
    unique_raw = base_raw + micro
    return f"{unique_raw / 10 ** USDT_DECIMALS:.6f}"


# ─────────────────────────────────────────────
#  Schemas
# ─────────────────────────────────────────────
class CreateInvoiceRequest(BaseModel):
    package_id: str


class VerifyTxRequest(BaseModel):
    order_id: str
    tx_hash: str


# ─────────────────────────────────────────────
#  Endpoints
# ─────────────────────────────────────────────
@router.post("/payments/erc20/create-invoice")
async def create_erc20_invoice(
    req: CreateInvoiceRequest,
    background_tasks: BackgroundTasks,
    user_info: dict = Depends(get_current_user_info),
):
    """
    Create a USDT ERC20 payment invoice.
    Returns exact amount, wallet address, and order ID.
    """
    pkg = PACKAGES.get(req.package_id)
    if not pkg:
        raise HTTPException(status_code=400, detail=f"Package tidak dikenal: {req.package_id}")

    user_id  = user_info["user_id"]

    # ── ADMIN INSTANT BYPASS ───────────────────────────────────────────────────
    if user_info.get("is_admin"):
        r = await _get_redis()
        credits = pkg["credits"]
        current = int(await r.get(f"user:{user_id}:credits") or 0)
        await r.set(f"user:{user_id}:credits", current + credits)
        plan_name = pkg.get("plan", "")
        if plan_name:
            await r.set(f"user:{user_id}:plan", plan_name)
        return {
            "status": "activated",
            "admin_bypass": True,
            "message": f"✅ {pkg['label']} langsung diaktifkan untuk admin!",
            "credits_added": credits,
            "new_plan": plan_name or None,
            "package": pkg["label"],
            "order_id": f"admin-{req.package_id}-{int(time.time())}",
        }
    ts       = int(time.time())
    order_id = f"GAS-{user_id[:8]}-{ts}"
    amount   = _unique_amount(pkg["price_usd"], order_id)
    expires  = ts + INVOICE_TTL_SEC
    expires_dt = datetime.fromtimestamp(expires, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    pending = {
        "order_id":    order_id,
        "user_id":     user_id,
        "package_id":  req.package_id,
        "credits":     pkg["credits"],
        "plan":        pkg.get("plan", ""),
        "label":       pkg["label"],
        "amount_usdt": amount,
        "amount_raw":  _usdt_raw(amount),
        "expires_at":  expires,
        "status":      "pending",
        "created_at":  datetime.utcnow().isoformat(),
    }

    r = await _get_redis()
    # Store by order_id and by amount for reverse lookup
    await r.set(f"erc20:order:{order_id}", json.dumps(pending), ex=INVOICE_TTL_SEC + 300)
    await r.set(f"erc20:amount:{_usdt_raw(amount)}", order_id, ex=INVOICE_TTL_SEC + 300)
    # Auto-register email from JWT and send invoice email immediately
    user_email_key = f"user:{user_id}:email"
    user_email = user_info.get("email", "") or await r.get(user_email_key) or ""
    username = user_info.get("username", "") or await r.get(f"user:{user_id}:username") or user_id

    # Persist email in Redis for future lookups
    if user_email:
        await r.set(user_email_key, user_email, ex=86400 * 30)
    if username:
        await r.set(f"user:{user_id}:username", username, ex=86400 * 30)

    # Send invoice email immediately to user so they can pay quickly
    if user_email:
        background_tasks.add_task(
            _send_invoice_email_bg,
            user_email, username or user_id, order_id, pkg["label"],
            amount, WALLET_ADDRESS, expires_dt, pkg["credits"], pkg.get("plan", "")
        )

    return {
        "status":          "ok",
        "order_id":        order_id,
        "wallet_address":  WALLET_ADDRESS,
        "amount_usdt":     amount,
        "network":         "Ethereum (ERC-20)",
        "token":           "USDT",
        "contract":        USDT_CONTRACT,
        "expires_at":      expires_dt,
        "expires_unix":    expires,
        "package":         pkg["label"],
        "credits":         pkg["credits"],
        "plan":            pkg.get("plan", ""),
        "instructions": (
            f"Kirim TEPAT {amount} USDT ke {WALLET_ADDRESS} "
            f"melalui jaringan Ethereum (ERC-20). "
            f"Pembayaran akan terdeteksi otomatis dalam 1-5 menit."
        ),
        "bank_account": BANK_ACCOUNT,
    }


@router.post("/payments/erc20/verify")
async def verify_erc20_tx(
    req: VerifyTxRequest,
    background_tasks: BackgroundTasks,
    user_info: dict = Depends(get_current_user_info),
):
    """
    Manually verify a USDT ERC20 transaction by tx_hash.
    Faster than waiting for the background poller.
    """
    r = await _get_redis()
    raw = await r.get(f"erc20:order:{req.order_id}")
    if not raw:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan atau sudah kadaluarsa")

    pending = json.loads(raw)
    if pending["user_id"] != user_info["user_id"]:
        raise HTTPException(status_code=403, detail="Order bukan milik Anda")
    if pending["status"] == "completed":
        return {"status": "already_completed", "detail": "Pembayaran sudah dikonfirmasi sebelumnya"}

    # Query Etherscan for this tx
    tx_data = await _fetch_tx_from_etherscan(req.tx_hash)
    if not tx_data:
        raise HTTPException(status_code=400, detail="TX hash tidak ditemukan di Etherscan")

    result = await _process_tx(tx_data, r, explicit_order_id=req.order_id, background_tasks=background_tasks)
    if result["status"] == "ok":
        return {"status": "confirmed", "detail": "Pembayaran berhasil dikonfirmasi", **result}

    raise HTTPException(status_code=400, detail=result.get("detail", "TX tidak cocok dengan invoice"))


@router.get("/payments/erc20/status/{order_id}")
async def get_erc20_order_status(
    order_id: str,
    user_info: dict = Depends(get_current_user_info),
):
    """Check the current status of an ERC20 payment order."""
    r = await _get_redis()
    raw = await r.get(f"erc20:order:{order_id}")
    if not raw:
        return {"status": "not_found", "detail": "Invoice tidak ditemukan atau sudah kadaluarsa"}

    pending = json.loads(raw)
    if pending["user_id"] != user_info["user_id"] and not user_info["is_admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    now = int(time.time())
    is_expired = now > pending.get("expires_at", 0) and pending["status"] == "pending"
    return {
        "order_id":    order_id,
        "status":      "expired" if is_expired else pending["status"],
        "amount_usdt": pending["amount_usdt"],
        "package":     pending["label"],
        "credits":     pending["credits"],
        "plan":        pending.get("plan", ""),
        "expires_at":  pending.get("expires_at"),
        "wallet":      WALLET_ADDRESS,
    }


@router.get("/payments/erc20/packages")
async def get_erc20_packages():
    """List all purchasable packages with ERC20 USDT price."""
    plans     = [{"id": k, **v} for k, v in PACKAGES.items() if k.startswith("plan_")]
    topups    = [{"id": k, **v} for k, v in PACKAGES.items() if k.startswith("topup_")]
    boosters  = [{"id": k, **v} for k, v in PACKAGES.items() if k.startswith("booster_")]
    return {
        "wallet":   WALLET_ADDRESS,
        "token":    "USDT ERC-20",
        "network":  "Ethereum",
        "plans":    plans,
        "topups":   topups,
        "boosters": boosters,
    }


@router.get("/payments/erc20/history")
async def get_erc20_history(user_info: dict = Depends(get_current_user_info)):
    """Get user ERC20 payment history."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    raw_list = await r.lrange(f"user:{user_id}:erc20_transactions", 0, 19)
    return {"transactions": [json.loads(t) for t in raw_list]}


# ─────────────────────────────────────────────
#  Etherscan helpers
# ─────────────────────────────────────────────
async def _fetch_latest_usdt_txs(block_from: int = 0) -> list:
    """Fetch recent USDT ERC-20 transfers TO our wallet via Etherscan."""
    params = {
        "chainid":         ETHERSCAN_CHAIN,
        "module":          "account",
        "action":          "tokentx",
        "address":         WALLET_ADDRESS,
        "contractaddress": USDT_CONTRACT,
        "startblock":      block_from,
        "endblock":        "latest",
        "sort":            "desc",
        "page":            1,
        "offset":          50,
        "apikey":          ETHERSCAN_API_KEY,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(ETHERSCAN_BASE, params=params)
            data = resp.json()
            result = data.get("result", [])
            # status "1" = found, "0" with list result = no transactions (not an error)
            if isinstance(result, list):
                return result
            logger.error(f"Etherscan unexpected result: {data.get('message')}")
    except Exception as e:
        logger.error(f"Etherscan fetch error: {e}")
    return []


async def _fetch_tx_from_etherscan(tx_hash: str) -> Optional[dict]:
    """Fetch a single token transaction by tx hash."""
    params = {
        "chainid": ETHERSCAN_CHAIN,
        "module":  "proxy",
        "action":  "eth_getTransactionByHash",
        "txhash":  tx_hash,
        "apikey":  ETHERSCAN_API_KEY,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(ETHERSCAN_BASE, params=params)
            data = resp.json()
            tx = data.get("result")
            if tx and tx.get("to", "").lower() == USDT_CONTRACT.lower():
                # Build compatible dict from raw tx
                return {"hash": tx_hash, "raw": tx}
    except Exception as e:
        logger.error(f"Etherscan tx lookup error: {e}")
    # Also try tokentx for the hash
    params2 = {
        "chainid":         ETHERSCAN_CHAIN,
        "module":          "account",
        "action":          "tokentx",
        "address":         WALLET_ADDRESS,
        "contractaddress": USDT_CONTRACT,
        "startblock":      0,
        "endblock":        "latest",
        "sort":            "desc",
        "page":            1,
        "offset":          100,
        "apikey":          ETHERSCAN_API_KEY,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(ETHERSCAN_BASE, params=params2)
            data = resp.json()
            if data.get("status") == "1":
                for tx in (data.get("result") or []):
                    if tx.get("hash", "").lower() == tx_hash.lower():
                        return tx
    except Exception as e:
        logger.error(f"Etherscan tokentx lookup error: {e}")
    return None


# ─────────────────────────────────────────────
#  Core: process a confirmed TX
# ─────────────────────────────────────────────
async def _process_tx(
    tx: dict,
    r: aioredis.Redis,
    explicit_order_id: str = None,
    background_tasks: BackgroundTasks = None,
) -> dict:
    """
    Match an incoming USDT tx to a pending order and fulfil it.
    Returns {"status": "ok", ...} on success, {"status": "no_match"} otherwise.
    """
    # Normalize tx fields (tokentx vs raw tx format)
    tx_hash  = tx.get("hash", "")
    to_addr  = tx.get("to", "").lower()
    raw_val  = int(tx.get("value", 0))
    tx_time  = int(tx.get("timeStamp", time.time()))

    # Guard: must be TO our wallet
    if to_addr and to_addr != WALLET_ADDRESS.lower():
        return {"status": "no_match", "detail": "TX bukan ke wallet GAS"}

    # Already processed?
    already_key = f"erc20:processed_tx:{tx_hash}"
    if await r.get(already_key):
        return {"status": "duplicate", "detail": "TX sudah diproses sebelumnya"}

    # Find order by amount
    order_id = explicit_order_id
    if not order_id:
        # Exact match first
        order_id = await r.get(f"erc20:amount:{raw_val}")
    if not order_id and not explicit_order_id:
        # Fuzzy match: try ±200 micro-USDT (0.0002 USDT) to handle wallet rounding.
        # This covers wallets that send 2.99 instead of 2.990058.
        for delta in range(1, 201):
            order_id = await r.get(f"erc20:amount:{raw_val + delta}")
            if order_id:
                break
            order_id = await r.get(f"erc20:amount:{raw_val - delta}")
            if order_id:
                break
    if not order_id:
        return {"status": "no_match", "detail": "Tidak ada invoice yang cocok dengan jumlah ini"}

    raw_pending = await r.get(f"erc20:order:{order_id}")
    if not raw_pending:
        return {"status": "no_match", "detail": "Invoice tidak ditemukan"}

    pending = json.loads(raw_pending)

    # Validate amount matches
    if explicit_order_id:
        # For manual verify: if raw_val is 0 it means the tx was fetched via
        # eth_getTransactionByHash (raw ETH tx format) which doesn't expose token
        # value at the top level. Since the user provided the order_id explicitly,
        # trust the order_id match and skip amount validation.
        # For proper tokentx format (raw_val > 0), apply ±100 unit tolerance (~0.0001 USDT).
        if raw_val > 0:
            diff = abs(raw_val - pending["amount_raw"])
            if diff > 100:
                return {
                    "status": "no_match",
                    "detail": f"Jumlah tidak sesuai. Diharapkan {pending['amount_usdt']} USDT"
                }
        # raw_val == 0: tx data from eth_getTransactionByHash — skip amount check

    if pending["status"] == "completed":
        return {"status": "duplicate", "detail": "Order sudah dikonfirmasi"}

    # Check not expired
    if int(time.time()) > pending.get("expires_at", 0):
        return {"status": "expired", "detail": "Invoice sudah kadaluarsa"}

    user_id   = pending["user_id"]
    credits   = int(pending["credits"])
    plan_name = pending.get("plan", "")
    label     = pending.get("label", "")
    amount_display = pending["amount_usdt"]

    # ── Fulfil order ──────────────────────────────────────
    # 1. Add credits
    credit_key = f"user:{user_id}:credits"
    current    = int((await r.get(credit_key)) or 0)
    new_total  = current + credits
    await r.set(credit_key, str(new_total))

    # 2. Activate plan with 30-day subscription expiry
    PLAN_DURATION_DAYS = 30
    plan_expires_ts = int(time.time()) + (PLAN_DURATION_DAYS * 86400)
    plan_expires_dt = datetime.fromtimestamp(plan_expires_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if plan_name:
        await r.set(f"user:{user_id}:plan", plan_name, ex=PLAN_DURATION_DAYS * 86400)
        await r.set(f"user:{user_id}:plan_expires_at", str(plan_expires_ts), ex=PLAN_DURATION_DAYS * 86400)
        await r.set(f"user:{user_id}:plan_expires_dt", plan_expires_dt, ex=PLAN_DURATION_DAYS * 86400)

    # 2b. Booster: add XP + set badge
    booster_xp = 0
    booster_badge = ""
    pkg_data = PACKAGES.get(pending.get("package_id", ""), {})
    if pending.get("package_id", "").startswith("booster_"):
        booster_xp = pkg_data.get("xp", 0)
        badge_days = pkg_data.get("badge_days", 7)
        badge_key = pending["package_id"].replace("booster_", "")  # bronze/silver/gold
        if booster_xp:
            cur_xp = int((await r.get(f"user:{user_id}:xp")) or 0)
            await r.set(f"user:{user_id}:xp", str(cur_xp + booster_xp))
        await r.set(f"user:{user_id}:booster", badge_key, ex=badge_days * 86400)
        await r.set(f"user:{user_id}:booster_expires_at",
                    str(int(time.time()) + badge_days * 86400), ex=badge_days * 86400)
        booster_badge = badge_key

    # Also add XP for plan purchases (50 XP per $1 spent)
    if plan_name and not pending.get("package_id", "").startswith("booster_"):
        try:
            plan_xp = int(float(pkg_data.get("price_usd", "0")) * 50)
            if plan_xp:
                cur_xp = int((await r.get(f"user:{user_id}:xp")) or 0)
                await r.set(f"user:{user_id}:xp", str(cur_xp + plan_xp))
        except Exception:
            pass

    # 3. Record transaction
    tx_record = {
        "order_id":    order_id,
        "user_id":     user_id,
        "package_id":  pending["package_id"],
        "label":       label,
        "credits":     credits,
        "amount_usdt": amount_display,
        "plan":        plan_name,
        "plan_expires_dt": plan_expires_dt if plan_name else "",
        "tx_hash":     tx_hash,
        "status":      "completed",
        "completed_at": datetime.utcnow().isoformat(),
    }
    await r.lpush(f"user:{user_id}:erc20_transactions", json.dumps(tx_record))
    await r.ltrim(f"user:{user_id}:erc20_transactions", 0, 49)
    await r.lpush(f"user:{user_id}:transactions", json.dumps(tx_record))
    await r.ltrim(f"user:{user_id}:transactions", 0, 49)

    # 4. Mark order completed
    pending["status"]       = "completed"
    pending["tx_hash"]      = tx_hash
    pending["completed_at"] = datetime.utcnow().isoformat()
    await r.set(f"erc20:order:{order_id}", json.dumps(pending), ex=86400 * 7)

    # 5. Mark tx as processed (avoid double credit)
    await r.set(already_key, "1", ex=86400 * 30)

    # 6. Send confirmation email if user email is stored
    user_email = await r.get(f"user:{user_id}:email") or ""
    username   = await r.get(f"user:{user_id}:username") or user_id

    _plan_exp = plan_expires_dt if plan_name else ""

    if user_email and background_tasks:
        background_tasks.add_task(
            _send_confirmation_email_bg,
            user_email, username, order_id, label,
            amount_display, credits, new_total, plan_name, tx_hash, _plan_exp
        )
    elif user_email:
        asyncio.create_task(
            _async_send_confirmation(
                user_email, username, order_id, label,
                amount_display, credits, new_total, plan_name, tx_hash, _plan_exp
            )
        )

    # Notify admin
    admin_email = os.getenv("ADMIN_EMAIL", "admin@gasstrategyai.xyz")
    asyncio.create_task(_notify_admin_payment(admin_email, username, user_email, order_id, label, amount_display, tx_hash))

    logger.info(
        f"ERC20 payment confirmed | order={order_id} user={user_id} "
        f"credits={credits} plan={plan_name} expires={_plan_exp} tx={tx_hash[:12]}..."
    )

    return {
        "status":        "ok",
        "order_id":      order_id,
        "credits_added": credits,
        "new_balance":   new_total,
        "plan_expires":  _plan_exp,
        "plan":          plan_name,
        "tx_hash":       tx_hash,
        "booster":       booster_badge,
        "booster_xp":    booster_xp,
    }


# ─────────────────────────────────────────────
#  Background poller (started at app startup)
# ─────────────────────────────────────────────
_poller_running = False


async def start_erc20_poller():
    """Background task: polls Etherscan every 60s for new USDT payments."""
    global _poller_running
    if _poller_running:
        return
    _poller_running = True
    logger.info("ERC20 poller started")

    last_block = 0
    while True:
        try:
            await asyncio.sleep(POLL_INTERVAL_SEC)
            txs = await _fetch_latest_usdt_txs(block_from=last_block)
            if txs:
                r = await _get_redis()
                for tx in txs:
                    block_num = int(tx.get("blockNumber", 0))
                    if block_num > last_block:
                        last_block = block_num
                    if tx.get("to", "").lower() == WALLET_ADDRESS.lower():
                        result = await _process_tx(tx, r)
                        if result["status"] == "ok":
                            logger.info(f"Auto-confirmed payment: {result}")
        except asyncio.CancelledError:
            _poller_running = False
            logger.info("ERC20 poller stopped")
            break
        except Exception as e:
            logger.error(f"ERC20 poller error: {e}")


# ─────────────────────────────────────────────
#  Email background helpers
# ─────────────────────────────────────────────
def _send_invoice_email_bg(
    email, username, order_id, label, amount, wallet, expires_dt, credits, plan
):
    try:
        from ...utils.email import send_invoice_email
        send_invoice_email(email, username, order_id, label, amount, wallet, expires_dt, credits, plan)
    except Exception as e:
        logger.error(f"Invoice email error: {e}")


def _send_confirmation_email_bg(
    email, username, order_id, label, amount, credits, new_balance, plan, tx_hash, plan_expires=""
):
    try:
        from ...utils.email import send_payment_confirmation_email
        send_payment_confirmation_email(
            email, username, order_id, label, amount, credits, new_balance, plan, tx_hash, plan_expires
        )
    except Exception as e:
        logger.error(f"Confirmation email error: {e}")


async def _async_send_confirmation(
    email, username, order_id, label, amount, credits, new_balance, plan, tx_hash, plan_expires=""
):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, _send_confirmation_email_bg,
        email, username, order_id, label, amount, credits, new_balance, plan, tx_hash, plan_expires
    )


async def _notify_admin_payment(admin_email, username, user_email, order_id, label, amount, tx_hash):
    """Send admin notification email when a payment is confirmed."""
    try:
        from ...utils.email import send_email
        subject = f"💰 Pembayaran Masuk — {label} ({amount} USDT)"
        short_tx = f"{tx_hash[:10]}...{tx_hash[-6:]}" if tx_hash and len(tx_hash) > 16 else tx_hash
        etherscan_url = f"https://etherscan.io/tx/{tx_hash}" if tx_hash else "#"
        body = f"""
        <div style="font-family:Arial,sans-serif;background:#060C18;color:#E2E8F0;padding:24px;border-radius:12px;">
        <h2 style="color:#F5A623;">💰 Pembayaran ERC20 USDT Dikonfirmasi</h2>
        <table style="width:100%;border-collapse:collapse;">
          <tr><td style="color:#718096;padding:6px 0;">Order ID</td><td style="color:#F5A623;font-family:monospace;">{order_id}</td></tr>
          <tr><td style="color:#718096;padding:6px 0;">User</td><td><b>{username}</b> ({user_email})</td></tr>
          <tr><td style="color:#718096;padding:6px 0;">Paket</td><td>{label}</td></tr>
          <tr><td style="color:#718096;padding:6px 0;">Jumlah</td><td style="color:#10B981;font-size:20px;font-weight:bold;">{amount} USDT</td></tr>
          <tr><td style="color:#718096;padding:6px 0;">TX Hash</td><td style="font-family:monospace;color:#60a5fa;">
            <a href="{etherscan_url}" style="color:#60a5fa;">{short_tx}</a></td></tr>
        </table>
        <p style="margin-top:16px;color:#4A5568;font-size:12px;">
          🤖 Auto-confirmed by GAS ERC20 poller · {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
        </p>
        </div>"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_email, admin_email, subject, body)
    except Exception as e:
        logger.error(f"Admin notify error: {e}")


# ─────────────────────────────────────────────
#  Admin: store user email for notifications
# ─────────────────────────────────────────────
class StoreEmailRequest(BaseModel):
    email: str


@router.post("/payments/erc20/register-email")
async def register_user_email(
    req: StoreEmailRequest,
    user_info: dict = Depends(get_current_user_info),
):
    """Store user email in Redis so payment confirmations can be emailed."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    await r.set(f"user:{user_id}:email", req.email)
    return {"status": "ok", "message": "Email tersimpan untuk notifikasi pembayaran"}
