import json
import redis.asyncio as aioredis
from typing import Any, Optional
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

class RedisCache:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        logger.info(f"Connected to Redis at {settings.REDIS_URL}")

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> dict | None:
        if not self.redis:
            return None
        val = await self.redis.get(key)
        return json.loads(val) if val else None

    async def set(self, key: str, value: dict, ttl: int = settings.CACHE_TTL):
        if not self.redis:
            return
        await self.redis.set(key, json.dumps(value), ex=ttl)

cache = RedisCache()
