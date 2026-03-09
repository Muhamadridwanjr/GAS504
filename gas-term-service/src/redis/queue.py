import json
import redis.asyncio as redis
from src.config import settings
from src.lib.logger import logger

class OrderQueue:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url)

    async def enqueue_order(self, order_dict: dict):
        try:
            await self.redis.lpush(settings.order_queue_key, json.dumps(order_dict))
            logger.info(f"Order {order_dict['id']} enqueued successfully")
        except Exception as e:
            logger.error(f"Failed to enqueue order to redis: {e}")
            raise

order_queue = OrderQueue()
