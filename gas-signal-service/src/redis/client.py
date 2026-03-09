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

    async def publish_signal(self, channel: str, signal_data: dict):
        if not self.redis:
            await self.connect()
        try:
            message = json.dumps(signal_data, default=default_json_serializer)
            await self.redis.publish(channel, message)
            logger.debug(f"Published signal to channel {channel}")
        except Exception as e:
            logger.error(f"Failed to publish signal: {e}")

redis_client = RedisClient()
