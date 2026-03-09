import redis.asyncio as redis
from src.config import settings
from src.utils.logger import logger

class RedisClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            await self.client.ping()
            logger.info("Connected to Redis", host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise e

    async def close(self):
        if self.client:
            await self.client.close()
            logger.info("Closed Redis connection")

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        await self.client.set(key, value, ex=expire)

    async def incr(self, key: str):
        return await self.client.incr(key)

    async def expire(self, key: str, seconds: int):
        return await self.client.expire(key, seconds)

    async def pipeline(self):
        return self.client.pipeline()

redis_client = RedisClient()
