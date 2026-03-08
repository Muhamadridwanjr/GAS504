from fastapi import APIRouter, HTTPException, Request
from src.services.redis import redis_service
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/terminal", tags=["Terminal EA"])

@router.get("/order/queue")
async def get_order_queue():
    """Poll the next order from the Redis queue."""
    try:
        order = await redis_service.get_next_order()
        if not order:
            return {} # EA expects empty if no order
        return order
    except Exception as e:
        logger.error("error_polling_order", error=str(e))
        return {} # Fallback for EA

@router.post("/order/status")
async def report_order_status(status_data: dict):
    """Receive order status from EA."""
    try:
        await redis_service.update_order_status(status_data)
        return {"status": "ok"}
    except Exception as e:
        logger.error("error_reporting_status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
