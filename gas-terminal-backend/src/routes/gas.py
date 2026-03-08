"""
GAS Terminal Backend – EA Integration Endpoints
These routes handle all communication from GASSTRATEGYEAPRO v4.0 EA.

EA → Gateway /api/gas/{path} → here at /terminal/gas/{path}
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import APIRouter, Query, HTTPException

from src.config import settings
from src.services.client import fetch_json, get_client
from src.services.redis import redis_service

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/terminal/gas", tags=["GAS EA"])


# ─────────────────────────────────────────────────────────────────────
# POST /terminal/gas/context
# EA sends full account+market+rules context every 30s
# ─────────────────────────────────────────────────────────────────────
@router.post("/context")
async def receive_ea_context(payload: dict):
    """Store EA context in Redis and broadcast to realtime hub."""
    try:
        symbol = payload.get("symbol", "XAUUSD")
        await redis_service.connect()

        # Store context with 90s TTL
        key = f"gas:context:{symbol}"
        await redis_service.client.set(key, json.dumps(payload), ex=90)

        # Also store a generic "latest" key
        await redis_service.client.set("gas:context:latest", json.dumps(payload), ex=90)

        # Publish to realtime hub subscribers
        pub_data = json.dumps({
            "channel": "ea:context",
            "data": {
                "symbol": symbol,
                "trader": payload.get("trader"),
                "balance_idr": payload.get("account", {}).get("balance_idr"),
                "daily_trades": payload.get("daily_stats", {}).get("trade_count"),
                "is_paused": payload.get("daily_stats", {}).get("is_paused"),
                "kill_zone": payload.get("kill_zone", {}),
                "positions": payload.get("positions", []),
                "timestamp": payload.get("timestamp"),
            }
        })
        await redis_service.client.publish("system:ea_context", pub_data)

        logger.info("ea_context_received", symbol=symbol,
                    trader=payload.get("trader"),
                    daily_trades=payload.get("daily_stats", {}).get("trade_count"))
        return {"status": "ok"}
    except Exception as e:
        logger.error("ea_context_error", error=str(e))
        return {"status": "ok"}  # Always return ok so EA doesn't retry-flood


# ─────────────────────────────────────────────────────────────────────
# POST /terminal/gas/signal/request
# EA POSTs full context → we call quant-orch → return GAS AI signal
# ─────────────────────────────────────────────────────────────────────
@router.post("/signal/request")
async def request_gas_signal(payload: dict):
    """
    EA sends full GAS context → terminal calls quant-orch → returns GAS AI signal.
    Signal format expected by EA:
    {
      signal_id, action, symbol, entry, sl, tp1, tp_final, lot,
      reason, observation, trading_plan, risk_management,
      journal, backtest, psychology, mindset,
      regime, session, confidence
    }
    """
    symbol = payload.get("symbol", "XAUUSD")
    market = payload.get("market", {})
    daily_stats = payload.get("daily_stats", {})
    rules = payload.get("rules", {})
    kill_zone = payload.get("kill_zone", {})
    positions = payload.get("positions", [])

    # If EA is paused or max trades reached, return NONE immediately
    if daily_stats.get("is_paused"):
        return _none_signal(symbol, "EA currently paused")

    max_trades = daily_stats.get("max_trades", 10)
    trade_count = daily_stats.get("trade_count", 0)
    if trade_count >= max_trades:
        return _none_signal(symbol, f"Max trades/day reached ({trade_count}/{max_trades})")

    no_layering = rules.get("no_layering", True)
    if no_layering and len(positions) > 0:
        return _none_signal(symbol, "No layering: active position exists")

    # Determine active session
    session = _detect_session(kill_zone)

    try:
        # Call quant-orch to generate signal
        quant_payload = {
            "symbol": symbol,
            "timeframe": "M15",
            "market": market,
            "session": session,
            "context": {
                "balance_usd": payload.get("account", {}).get("balance_usd", 0),
                "daily_pnl_usd": daily_stats.get("pnl_usd", 0),
                "consecutive_loss": daily_stats.get("consecutive_loss", 0),
                "fixed_lot": rules.get("fixed_lot", 0.01),
                "max_spread": rules.get("max_spread", 5000),
            }
        }
        signal = await fetch_json(
            f"{settings.QUANT_ORCH_URL}/signal/generate",
            method="POST",
            json_body=quant_payload,
            timeout=10.0,
        )

        if "error" in signal or signal.get("action") in (None, "NONE", "WAIT", ""):
            return _none_signal(symbol, signal.get("error", "No signal from quant engine"))

        # Cache signal in Redis (90s TTL)
        await redis_service.connect()
        cache_key = f"gas:signal:latest:{symbol}"
        await redis_service.client.set(cache_key, json.dumps(signal), ex=90)
        await redis_service.client.set("gas:signal:latest", json.dumps(signal), ex=90)

        # Publish new signal to realtime hub
        pub_data = json.dumps({
            "channel": "signal:new",
            "data": signal
        })
        await redis_service.client.publish("signal:gas_ai", pub_data)

        logger.info("gas_signal_generated",
                    symbol=symbol,
                    action=signal.get("action"),
                    confidence=signal.get("confidence"),
                    session=session)
        return signal

    except Exception as e:
        logger.error("gas_signal_request_error", error=str(e))
        return _none_signal(symbol, f"Engine error: {str(e)}")


# ─────────────────────────────────────────────────────────────────────
# GET /terminal/gas/signal/latest
# EA polls for last cached signal
# ─────────────────────────────────────────────────────────────────────
@router.get("/signal/latest")
async def get_latest_gas_signal(symbol: str = Query("XAUUSD")):
    """Return last cached GAS AI signal from Redis."""
    try:
        await redis_service.connect()
        raw = await redis_service.client.get(f"gas:signal:latest:{symbol}")
        if not raw:
            raw = await redis_service.client.get("gas:signal:latest")
        if raw:
            return json.loads(raw)
        return _none_signal(symbol, "No cached signal")
    except Exception as e:
        logger.error("get_latest_signal_error", error=str(e))
        return _none_signal(symbol, str(e))


# ─────────────────────────────────────────────────────────────────────
# POST /terminal/gas/journal
# EA sends trade journal after every closed position
# ─────────────────────────────────────────────────────────────────────
@router.post("/journal")
async def receive_trade_journal(payload: dict):
    """Forward EA trade journal to gas-journal-service."""
    try:
        # Map EA journal format to internal journal format
        direction = payload.get("direction", "SELL")
        profit_usd = payload.get("profit_usd", 0)
        symbol = payload.get("symbol", "UNKNOWN")

        internal_payload = {
            "symbol": symbol,
            "direction": direction,
            "entry_price": payload.get("deal_price", 0),
            "exit_price": payload.get("deal_price", 0),
            "volume": payload.get("volume", 0),
            "profit": profit_usd,
            "commission": 0,
            "swap": 0,
            "result": payload.get("result", "WIN" if profit_usd >= 0 else "LOSS"),
            "source": f"EA:{payload.get('trader', 'unknown')}",
            "notes": json.dumps({
                "profit_idr": payload.get("profit_idr"),
                "daily_count": payload.get("daily_count"),
                "daily_pnl_idr": payload.get("daily_pnl_idr"),
                "consecutive_loss": payload.get("consecutive_loss"),
                "kill_zone_london": payload.get("kill_zone_london"),
                "kill_zone_ny": payload.get("kill_zone_ny"),
                "balance_after": payload.get("balance_after"),
                "balance_idr_after": payload.get("balance_idr_after"),
            }),
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "closed_at": datetime.now(timezone.utc).isoformat(),
        }

        # Try forwarding to journal service
        result = await fetch_json(
            f"{settings.JOURNAL_URL}/internal/trades",
            method="POST",
            json_body=internal_payload,
            headers={"X-API-Key": settings.GATEWAY_API_KEY},
            timeout=5.0,
        )

        # Also publish to Redis for real-time dashboard update
        await redis_service.connect()
        pub_data = json.dumps({
            "channel": "journal:new_trade",
            "data": {**payload, "type": "ea_journal"}
        })
        await redis_service.client.publish("notification:journal", pub_data)

        logger.info("ea_journal_received",
                    symbol=symbol,
                    result=payload.get("result"),
                    profit_usd=profit_usd,
                    trader=payload.get("trader"))
        return {"status": "ok", "journal_id": result.get("id") if "error" not in result else None}
    except Exception as e:
        logger.error("ea_journal_error", error=str(e))
        return {"status": "ok"}


# ─────────────────────────────────────────────────────────────────────
# POST /terminal/gas/alert/pause
# EA sends alert when trading is paused (3x loss or max daily loss)
# ─────────────────────────────────────────────────────────────────────
@router.post("/alert/pause")
async def receive_pause_alert(payload: dict):
    """Store pause alert and broadcast to dashboard."""
    try:
        await redis_service.connect()

        alert_data = {
            "type": "EA_PAUSE",
            "trader": payload.get("trader"),
            "reason": payload.get("reason"),
            "consecutive_loss": payload.get("consecutive_loss"),
            "daily_pnl_idr": payload.get("daily_pnl_idr"),
            "max_loss_idr": payload.get("max_loss_idr"),
            "pause_until": payload.get("pause_until"),
            "timestamp": payload.get("timestamp", int(datetime.now(timezone.utc).timestamp())),
        }

        # Store latest pause alert
        await redis_service.client.set(
            "gas:alert:pause:latest",
            json.dumps(alert_data),
            ex=86400  # 24h
        )

        # Push to alert list (keep last 50)
        await redis_service.client.lpush("gas:alerts:pause", json.dumps(alert_data))
        await redis_service.client.ltrim("gas:alerts:pause", 0, 49)

        # Broadcast to realtime hub
        pub_data = json.dumps({
            "channel": "alert:ea_pause",
            "data": alert_data
        })
        await redis_service.client.publish("notification:ea_pause", pub_data)

        logger.warning("ea_pause_alert",
                       trader=payload.get("trader"),
                       reason=payload.get("reason"),
                       consecutive_loss=payload.get("consecutive_loss"))
        return {"status": "ok"}
    except Exception as e:
        logger.error("ea_pause_alert_error", error=str(e))
        return {"status": "ok"}


# ─────────────────────────────────────────────────────────────────────
# POST /terminal/gas/signal/confirm
# EA confirms it executed a GAS AI signal
# ─────────────────────────────────────────────────────────────────────
@router.post("/signal/confirm")
async def confirm_signal_execution(payload: dict):
    """Store signal execution confirmation and update dashboard."""
    try:
        signal_id = payload.get("signal_id", str(uuid.uuid4()))
        await redis_service.connect()

        confirm_data = {
            "signal_id": signal_id,
            "action": payload.get("action"),
            "symbol": payload.get("symbol"),
            "lot": payload.get("lot"),
            "sl": payload.get("sl"),
            "tp": payload.get("tp"),
            "executed_by": payload.get("executed_by"),
            "reason": payload.get("reason"),
            "timestamp": payload.get("timestamp"),
            "confirmed_at": int(datetime.now(timezone.utc).timestamp()),
        }

        # Store confirmation
        key = f"gas:signal:confirm:{signal_id}"
        await redis_service.client.set(key, json.dumps(confirm_data), ex=86400)

        # Broadcast
        pub_data = json.dumps({
            "channel": "signal:confirmed",
            "data": confirm_data
        })
        await redis_service.client.publish("signal:gas_confirmed", pub_data)

        logger.info("signal_execution_confirmed",
                    signal_id=signal_id,
                    action=payload.get("action"),
                    symbol=payload.get("symbol"))
        return {"status": "ok", "signal_id": signal_id}
    except Exception as e:
        logger.error("signal_confirm_error", error=str(e))
        return {"status": "ok"}


# ─────────────────────────────────────────────────────────────────────
# GET /terminal/gas/context/latest
# Dashboard polls EA context for display
# ─────────────────────────────────────────────────────────────────────
@router.get("/context/latest")
async def get_latest_ea_context(symbol: str = Query("XAUUSD")):
    """Return last EA context from Redis (for dashboard display)."""
    try:
        await redis_service.connect()
        raw = await redis_service.client.get(f"gas:context:{symbol}")
        if not raw:
            raw = await redis_service.client.get("gas:context:latest")
        if raw:
            return json.loads(raw)
        return {"status": "no_data", "message": "No EA context received yet"}
    except Exception as e:
        logger.error("get_ea_context_error", error=str(e))
        return {"status": "error", "message": str(e)}


# ─────────────────────────────────────────────────────────────────────
# GET /terminal/gas/alerts
# Dashboard: get last N pause alerts
# ─────────────────────────────────────────────────────────────────────
@router.get("/alerts")
async def get_pause_alerts(limit: int = Query(10, le=50)):
    """Return recent EA pause alerts."""
    try:
        await redis_service.connect()
        raw_list = await redis_service.client.lrange("gas:alerts:pause", 0, limit - 1)
        alerts = [json.loads(r) for r in raw_list]
        return {"status": "ok", "alerts": alerts}
    except Exception as e:
        logger.error("get_alerts_error", error=str(e))
        return {"status": "ok", "alerts": []}


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────
def _none_signal(symbol: str, reason: str = "No signal") -> dict:
    return {
        "signal_id": "",
        "action": "NONE",
        "symbol": symbol,
        "entry": 0,
        "sl": 0,
        "tp1": 0,
        "tp_final": 0,
        "lot": 0,
        "reason": reason,
        "observation": "",
        "trading_plan": "",
        "risk_management": "",
        "journal": "",
        "backtest": "",
        "psychology": "Wait for valid setup. No FOMO.",
        "mindset": "Process > Profit. Trust the system.",
        "regime": "UNKNOWN",
        "session": "OFF",
        "confidence": 0,
    }


def _detect_session(kill_zone: dict) -> str:
    if kill_zone.get("london"):
        return "LONDON"
    if kill_zone.get("new_york"):
        return "NEW_YORK"
    return "OFF"
