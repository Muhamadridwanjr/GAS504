import json
import redis.asyncio as aioredis
from typing import Optional
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

cache = RedisCache()
