import json
import asyncio
import redis.asyncio as redis
from src.config import settings
from src.lib.logger import logger
from src.db.database import AsyncSessionLocal
from src.db.models import Order
from sqlalchemy import select

class StatusListener:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url)
        self.pubsub = self.redis.pubsub()

    async def start_listening(self):
        await self.pubsub.subscribe(settings.status_channel)
        logger.info(f"Subscribed to Redis channel: {settings.status_channel}")
        
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    data = message['data']
                    try:
                        status_update = json.loads(data)
                        await self.process_status_update(status_update)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode status message: {data}")
                    except Exception as e:
                        logger.error(f"Error processing status: {e}")
        except asyncio.CancelledError:
            logger.info("Listener cancelled")
        finally:
            await self.pubsub.unsubscribe(settings.status_channel)
            await self.redis.close()

    async def process_status_update(self, data: dict):
        order_id = data.get("order_id")
        status = data.get("status")
        
        if not order_id or not status:
            logger.warning(f"Invalid status payload: {data}")
            return
            
        logger.info(f"Processing status update for {order_id} -> {status}")
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Order).where(Order.id == order_id))
            order = result.scalar_one_or_none()
            
            if order:
                order.status = status
                order.fill_price = data.get("fill_price", order.fill_price)
                await session.commit()
                logger.info(f"Order {order_id} updated in DB to {status}")
                
                # If filled, here we would ideally call gas-journal-service
                if status == "filled":
                    # For brevity we log it. A background task or direct REST call can be placed here.
                    logger.info(f"Triggering journal logic for order {order_id}")
                    
            else:
                logger.warning(f"Order {order_id} not found in DB")

listener = StatusListener()
