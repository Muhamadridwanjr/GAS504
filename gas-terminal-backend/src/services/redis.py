import redis.asyncio as redis
import json
from src.config import settings
import structlog

logger = structlog.get_logger(__name__)

class RedisService:
    def __init__(self):
        self.client = None
        self._hot_client = None  # hot Redis for live MT5 tick prices

    async def connect(self):
        if not self.client:
            self.client = redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("connected_to_redis")

    async def connect_hot(self):
        """Connect to hot Redis (MT5 live tick prices, no AOF)."""
        if not self._hot_client:
            self._hot_client = redis.from_url(
                settings.REDIS_HOT_URL,
                encoding="utf-8",
                decode_responses=True,
            )

    async def get_market_price(self, symbol: str):
        """Read live market price from hot Redis (written by gas-mt5-websocket)."""
        await self.connect_hot()
        try:
            raw = await self._hot_client.get(f"market:{symbol.upper()}")
            return json.loads(raw) if raw else None
        except Exception:
            return None

    async def get_next_order(self):
        """Pop the next order from the queue."""
        await self.connect()
        order_json = await self.client.rpop("order:queue")
        if order_json:
            return json.loads(order_json)
        return None

    async def update_order_status(self, status_data: dict):
        """Store the order status reported by EA."""
        await self.connect()
        order_id = status_data.get("order_id")
        if order_id:
            key = f"order:status:{order_id}"
            await self.client.set(key, json.dumps(status_data), ex=86400) # Keep for 24h
            logger.info("order_status_updated", order_id=order_id, status=status_data.get("status"))

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None

redis_service = RedisService()
