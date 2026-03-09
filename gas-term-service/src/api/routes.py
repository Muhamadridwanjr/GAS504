from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.models import TradeRequest, StatusUpdate
from src.lib.logger import logger
from src.db.database import get_db
from src.core.order_manager import OrderManager

router = APIRouter()

@router.post("/trade")
async def place_order(
    request: TradeRequest,
    x_user_id: str = Header(..., alias="X-User-ID"),
    db: AsyncSession = Depends(get_db)
):
    try:
        manager = OrderManager(db)
        order = await manager.place_order(x_user_id, request)
        
        logger.info(f"Order {order.id} placed successfully for {x_user_id}")
        return {
            "order_id": order.id,
            "status": order.status,
            "message": "Order placed successfully"
        }
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders")
async def get_orders(x_user_id: str = Header(..., alias="X-User-ID")):
    return {"orders": []}

@router.get("/positions")
async def get_positions(x_user_id: str = Header(..., alias="X-User-ID")):
    return {"positions": []}

@router.post("/internal/status")
async def update_status(update: StatusUpdate):
    # Called internally or by EA Webhook occasionally
    logger.info(f"Received status update for {update.order_id}: {update.status}")
    return {"status": "ok"}
