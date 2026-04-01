"""
Portfolio Routes – Per-User MT5 Account Data
Reads user-specific account data from Redis (stored by per-user EA via /account-heartbeat).
Also reads global heartbeat for market EA data.
"""
import json
from datetime import datetime
from fastapi import APIRouter, Request
from src.services.redis import redis_service
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/terminal", tags=["Portfolio"])

KNOWN_SYMBOLS = [
    "XAUUSD", "BTCUSD", "EURUSD", "GBPUSD", "USDJPY",
    "ETHUSD", "XAGUSD", "US30", "US500", "DXY", "NAS100", "GBPJPY"
]


def _get_user_id_from_request(request: Request) -> str | None:
    """
    Extract user_id from the Authorization token.
    The auth middleware adds user info to request.state.
    """
    try:
        # Try from state set by auth middleware
        user = getattr(request.state, 'user', None)
        if user:
            return str(user.get('sub') or user.get('user_id') or user.get('id') or '')
    except Exception:
        pass
    # Fallback: get from query param (for testing)
    return request.query_params.get('user_id')


@router.get("/portfolio/live")
async def get_live_portfolio(request: Request):
    """
    Fetch live portfolio data for the logged-in user.
    Priority:
      1. Per-user EA data (from account:{user_id}) — most accurate, user-specific
      2. Global EA heartbeat (from heartbeat:{symbol}) — fallback, main EA data
    """
    try:
        await redis_service.connect()
        
        user_id = _get_user_id_from_request(request)
        
        # ── Try per-user account data first ──────────────────────────────
        if user_id:
            key_account = f"account:{user_id}"
            raw = await redis_service.client.get(key_account)
            if raw:
                try:
                    data = json.loads(raw)
                    # Check not too old (double-check TTL via last_update)
                    return {
                        "status": "live",
                        "source": "user_ea_heartbeat",
                        "user_id": user_id,
                        "account_id": data.get("account_id"),
                        "broker": data.get("broker", ""),
                        "server": data.get("server", ""),
                        "currency": data.get("currency", "USD"),
                        "leverage": data.get("leverage", 100),
                        "balance": float(data.get("balance", 0)),
                        "equity": float(data.get("equity", 0)),
                        "margin": float(data.get("margin", 0)),
                        "free_margin": float(data.get("free_margin", 0)),
                        "margin_level": float(data.get("margin_level", 0)),
                        "floating_pnl": float(data.get("floating_pnl", 0)),
                        "daily_pnl": float(data.get("daily_pnl", 0)),
                        "open_positions": int(data.get("positions_count", 0)),
                        "last_update": data.get("last_update"),
                        "ea_version": data.get("ea_version", ""),
                        "symbol": data.get("symbol", ""),
                    }
                except Exception as e:
                    logger.error("parse_user_account_error", error=str(e))

        # ── Fallback: global EA heartbeat (main EA) ──────────────────────
        best = None
        for symbol in KNOWN_SYMBOLS:
            key = f"heartbeat:{symbol}"
            raw = await redis_service.client.get(key)
            if raw:
                try:
                    data = json.loads(raw)
                    equity = float(data.get("equity", 0))
                    if best is None or equity > float(best.get("equity", 0)):
                        best = data
                        best["_symbol"] = symbol
                except Exception:
                    continue

        if best:
            balance = float(best.get("balance", 0))
            equity = float(best.get("equity", 0))
            return {
                "status": "live",
                "source": "main_ea_heartbeat",
                "user_id": user_id,
                "account_id": None,
                "broker": "",
                "server": "",
                "currency": "USD",
                "leverage": 100,
                "balance": balance,
                "equity": equity,
                "margin": 0,
                "free_margin": 0,
                "margin_level": 0,
                "floating_pnl": round(equity - balance, 2),
                "daily_pnl": 0,
                "open_positions": int(best.get("positions", 0)),
                "last_update": None,
                "ea_version": "",
                "symbol": best.get("_symbol", ""),
            }

        # ── No data available ────────────────────────────────────────────
        return {
            "status": "no_heartbeat",
            "source": None,
            "message": (
                "Heartbeat EA belum diterima. "
                "Pastikan EA GASSTRATEGYEAPRO berjalan dan user_id dikonfigurasi benar. "
                "Endpoint: POST /mt5/account-heartbeat"
            ),
            "balance": None,
            "equity": None,
            "floating_pnl": None,
            "open_positions": 0,
        }

    except Exception as e:
        logger.error("portfolio_fetch_error", error=str(e))
        return {
            "status": "error",
            "message": str(e),
            "balance": None,
            "equity": None,
            "open_positions": 0,
        }


@router.get("/portfolio/positions")
async def get_user_positions(request: Request):
    """
    Get open positions for the logged-in user.
    Reads from account:{user_id}:positions (set by per-user EA).
    """
    try:
        await redis_service.connect()
        user_id = _get_user_id_from_request(request)

        if user_id:
            key = f"account:{user_id}:positions"
            raw = await redis_service.client.get(key)
            if raw:
                try:
                    positions = json.loads(raw)
                    return {
                        "status": "ok",
                        "source": "user_ea",
                        "user_id": user_id,
                        "positions": positions,
                        "count": len(positions),
                    }
                except Exception:
                    pass

        # Fallback: no per-user EA data
        return {
            "status": "no_data",
            "source": None,
            "positions": [],
            "count": 0,
            "message": "Pasang EA per-user dan set user_id untuk melihat posisi terbuka.",
        }

    except Exception as e:
        logger.error("positions_fetch_error", error=str(e))
        return {"status": "error", "positions": [], "count": 0}


@router.get("/portfolio/account-status")
async def get_account_status(request: Request):
    """
    Check if the user has a per-user EA connected.
    Returns connection mode: 'user_ea' | 'main_ea' | 'offline'
    """
    await redis_service.connect()
    user_id = _get_user_id_from_request(request)
    has_user_ea = False
    has_main_ea = False

    if user_id:
        key = f"account:{user_id}"
        has_user_ea = bool(await redis_service.client.exists(key))
    
    for symbol in KNOWN_SYMBOLS[:3]:
        if await redis_service.client.exists(f"heartbeat:{symbol}"):
            has_main_ea = True
            break

    mode = "user_ea" if has_user_ea else ("main_ea" if has_main_ea else "offline")
    return {
        "mode": mode,
        "user_id": user_id,
        "has_user_ea": has_user_ea,
        "has_main_ea": has_main_ea,
    }
