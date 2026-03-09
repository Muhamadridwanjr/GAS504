import redis.asyncio as redis
from typing import Optional

from src.config import settings
from src.lib.logger import logger

class RedisCache:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Error reading from Redis {key}: {e}")
            return None

    async def set(self, key: str, value: str, expire: int = settings.CACHE_TTL) -> bool:
        try:
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Error writing to Redis {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting from Redis {key}: {e}")
            return False

    async def close(self):
        await self.redis.aclose()
