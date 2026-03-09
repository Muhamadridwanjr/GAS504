import redis.asyncio as redis
from src.config import settings
from src.lib.logger import log

class RedisClient:
    def __init__(self):
        self.url = settings.REDIS_URL
        self._redis = None

    @property
    def client(self):
        return self._redis

    async def connect(self):
        try:
            self._redis = redis.from_url(self.url, decode_responses=True)
            await self._redis.ping()
            log.info(f"Connected to Redis at {self.url}")
        except Exception as e:
            log.error(f"Failed to connect to Redis: {e}")
            raise

    async def close(self):
        if self._redis:
            await self._redis.close()
            log.info("Redis connection closed")

    async def publish(self, channel: str, message: str):
        if not self._redis:
            log.warning("Cannot publish, Redis is not connected")
            return
        
        try:
            await self._redis.publish(channel, message)
            log.debug(f"Published to {channel}: {message}")
        except Exception as e:
            log.error(f"Error publishing to {channel}: {e}")

redis_client = RedisClient()
