from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Order
from src.api.models import TradeRequest
from src.core.billing_client import billing_client
from src.core.risk_client import risk_client
from src.redis.queue import order_queue
from src.lib.logger import logger

class OrderManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def place_order(self, user_id: str, request: TradeRequest) -> Order:
        # 1. Billing check
        await billing_client.check_and_deduct_quota(user_id, "trade")
        
        # 2. Risk check
        risk_res = await risk_client.validate_order(user_id, request.model_dump())
        final_volume = risk_res.get("recommended_lot", request.volume)

        # 3. Create DB Record
        new_order = Order(
            user_id=user_id,
            symbol=request.symbol,
            action=request.action.value,
            order_type=request.order_type.value,
            volume=final_volume,
            req_price=request.price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            status="pending"
        )
        self.db.add(new_order)
        await self.db.commit()
        await self.db.refresh(new_order)
        
        # 4. Enqueue to Redis for MT5 Exec
        order_payload = {
            "id": new_order.id,
            "user_id": new_order.user_id,
            "symbol": new_order.symbol,
            "action": new_order.action,
            "order_type": new_order.order_type,
            "volume": new_order.volume,
            "price": new_order.req_price,
            "sl": new_order.stop_loss,
            "tp": new_order.take_profit
        }
        await order_queue.enqueue_order(order_payload)
        
        return new_order
