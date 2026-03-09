import json
import redis.asyncio as redis
from src.config import settings
from src.lib.logger import logger
from src.lib.utils import default_json_serializer


class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        try:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await self.redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")

    async def get_cached(self, key: str) -> dict | None:
        """Get cached data by key."""
        if not self.redis:
            return None
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None

    async def set_cached(self, key: str, data: dict, ttl: int = 300):
        """Cache data with TTL (default 5 minutes)."""
        if not self.redis:
            return
        try:
            serialized = json.dumps(data, default=default_json_serializer)
            await self.redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def invalidate(self, pattern: str):
        """Invalidate cache keys matching pattern."""
        if not self.redis:
            return
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                await self.redis.delete(*keys)
                logger.debug(f"Invalidated {len(keys)} cache keys for pattern: {pattern}")
        except Exception as e:
            logger.error(f"Redis invalidate error: {e}")

    async def publish_event(self, channel: str, data: dict):
        """Publish event to Redis channel."""
        if not self.redis:
            await self.connect()
        try:
            message = json.dumps(data, default=default_json_serializer)
            await self.redis.publish(channel, message)
            logger.debug(f"Published event to channel {channel}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")


redis_client = RedisClient()
