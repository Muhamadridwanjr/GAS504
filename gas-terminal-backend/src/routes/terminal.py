from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from src.services.redis import redis_service
import structlog
import json
import uuid
from datetime import datetime

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/terminal", tags=["Terminal EA"])


# ── Request Models ──────────────────────────────────────────────────────────
class SignalOrder(BaseModel):
    """A trade signal pushed by GAS AI features to the EA execution queue."""
    symbol: str                            # e.g. "XAUUSD"
    direction: str                         # "BUY" or "SELL"
    entry: float                           # Entry price
    sl: float                              # Stop Loss
    tp1: float                             # Take Profit 1
    tp2: Optional[float] = None            # Take Profit 2 (optional)
    tp3: Optional[float] = None            # Take Profit 3 (optional)
    lot: Optional[float] = None            # Lot size (if None, EA calculates)
    risk_pct: Optional[float] = 1.0        # Risk % if lot is auto-calculated
    max_slippage_pips: Optional[float] = 5.0  # Max acceptable slippage
    expiry_seconds: Optional[int] = 300    # Signal expires after N seconds
    grade: Optional[str] = "A"            # Signal grade (A+/A/B+)
    source: Optional[str] = "ai_signal"   # Which feature generated this
    magic: Optional[int] = 88888          # MT5 magic number for this EA
    comment: Optional[str] = "GAS_AI"
    user_id: Optional[str] = None         # If None, sends to all connected EAs


@router.get("/order/queue")
async def get_order_queue(user_id: Optional[str] = None):
    """
    Poll the next pending order from the Redis queue.
    EA calls this every 5 seconds. Returns {} if nothing pending.
    """
    try:
        await redis_service.connect()
        
        # Try user-specific queue first
        order = None
        if user_id:
            order_json = await redis_service.client.rpop(f"order:queue:{user_id}")
            if order_json:
                order = json.loads(order_json)
        
        # Fallback to global queue
        if not order:
            order = await redis_service.get_next_order()
        
        if not order:
            return {}
        return order
    except Exception as e:
        logger.error("error_polling_order", error=str(e))
        return {}


@router.post("/order/queue/push")
async def push_signal_to_queue(signal: SignalOrder):
    """
    Push an AI-generated trade signal to the EA execution queue.
    Called by GAS AI features (Signal view, Technical AI, etc.) when user clicks Execute.
    """
    try:
        await redis_service.connect()
        
        order_id = str(uuid.uuid4())[:8].upper()
        order = {
            "order_id": order_id,
            "symbol": signal.symbol,
            "direction": signal.direction.upper(),
            "entry": signal.entry,
            "sl": signal.sl,
            "tp1": signal.tp1,
            "tp2": signal.tp2,
            "tp3": signal.tp3,
            "lot": signal.lot,
            "risk_pct": signal.risk_pct,
            "max_slippage_pips": signal.max_slippage_pips,
            "expiry_seconds": signal.expiry_seconds,
            "grade": signal.grade,
            "source": signal.source,
            "magic": signal.magic or 88888,
            "comment": signal.comment or f"GAS_{signal.source or 'AI'}",
            "user_id": signal.user_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }
        
        # Push to user-specific or global queue
        queue_key = f"order:queue:{signal.user_id}" if signal.user_id else "order:queue"
        await redis_service.client.lpush(queue_key, json.dumps(order))
        
        # Store in pending orders (for status tracking)
        await redis_service.client.set(
            f"order:pending:{order_id}",
            json.dumps(order),
            ex=signal.expiry_seconds or 300
        )
        
        logger.info("signal_pushed", order_id=order_id, symbol=signal.symbol, direction=signal.direction)
        return {
            "status": "queued",
            "order_id": order_id,
            "message": f"Signal {signal.direction} {signal.symbol} antri untuk eksekusi EA"
        }
    except Exception as e:
        logger.error("error_pushing_signal", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/order/status")
async def report_order_status(status_data: dict):
    """Receive order execution status from EA."""
    try:
        await redis_service.update_order_status(status_data)
        return {"status": "ok"}
    except Exception as e:
        logger.error("error_reporting_status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/order/status/{order_id}")
async def get_order_status(order_id: str):
    """Get the execution status of a specific order."""
    try:
        await redis_service.connect()
        key = f"order:status:{order_id}"
        raw = await redis_service.client.get(key)
        if raw:
            return json.loads(raw)
        # Check if still pending
        pend = await redis_service.client.get(f"order:pending:{order_id}")
        if pend:
            return {**json.loads(pend), "status": "pending"}
        return {"status": "not_found", "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
