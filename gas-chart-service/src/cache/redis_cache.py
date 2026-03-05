import json
from typing import Any, Optional
import redis.asyncio as aioredis
from src.config import settings
from src.lib.logger import get_logger
logger = get_logger(__name__)
class RedisCache:
    def __init__(self): self._redis = None
    async def connect(self):
        try:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            await self._redis.ping(); logger.info("Redis connected")
        except Exception as e: logger.warning("Redis unavailable: %s", e); self._redis = None
    async def get(self, key):
        if not self._redis: return None
        try:
            d = await self._redis.get(key)
            return json.loads(d) if d else None
        except: return None
    async def set(self, key, value, ttl=None):
        if not self._redis: return
        try: await self._redis.set(key, json.dumps(value, default=str), ex=ttl or settings.CACHE_TTL)
        except: pass
    async def close(self):
        if self._redis: await self._redis.close()
