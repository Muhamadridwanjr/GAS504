import json
import redis.asyncio as redis
import logging
from ..config import settings

logger = logging.getLogger("publisher")

class Publisher:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        self.redis = redis.from_url(settings.redis_url)
        logger.info(f"Connected to Redis at {settings.redis_url}")

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def publish_tick(self, symbol: str, data: dict):
        if not self.redis:
            return
        
        message = {
            "type": "price",
            "symbol": symbol,
            "price": data.get("last", 0),
            "raw": data
        }
        
        # Publish to gas-realtime-hub via Redis pubsub channel
        # which will be forwarded to terminal ws frontends
        await self.redis.publish("market:ticks", json.dumps(message))
        
        # Also cache the latest price
        await self.redis.set(f"binance:ticker:{symbol}", json.dumps(data), ex=settings.cache_ttl)

publisher = Publisher()
