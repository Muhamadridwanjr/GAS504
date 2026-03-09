import json
import redis.asyncio as redis
from typing import Optional, Any
from src.config import settings
from src.lib.logger import logger

class RedisCache:
    def __init__(self):
        self.redis = None

    async def connect(self):
        if not self.redis:
            try:
                self.redis = redis.from_url(settings.redis_url, decode_responses=True)
                await self.redis.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.error(f"Redis connection error: {e}")
                self.redis = None

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        if not self.redis: return None
        try:
            val = await self.redis.get(key)
            if val:
                return json.loads(val)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: int = settings.cache_ttl):
        if not self.redis: return
        try:
            await self.redis.set(key, json.dumps(value), ex=ttl)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

cache = RedisCache()
