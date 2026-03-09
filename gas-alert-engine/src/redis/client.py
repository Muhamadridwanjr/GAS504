import json
import redis.asyncio as redis
from src.config import settings
from src.lib.logger import logger
from src.lib.utils import default_json_serializer


class RedisClient:
    """Async Redis client for pub/sub, cache, and queues."""

    def __init__(self):
        self.redis = None
        self.pubsub = None

    async def connect(self):
        try:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await self.redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
            logger.info("PubSub closed")
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")

    # ── Pub/Sub ──────────────────────────────────────────────
    async def subscribe(self, channel: str):
        """Subscribe to a Redis pub/sub channel and return the pubsub object."""
        if not self.redis:
            await self.connect()
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(channel)
        logger.info(f"Subscribed to channel: {channel}")
        return self.pubsub

    # ── Notification Queue ───────────────────────────────────
    async def push_notification(self, queue: str, data: dict):
        """Push a notification task to the Redis queue."""
        if not self.redis:
            await self.connect()
        try:
            message = json.dumps(data, default=default_json_serializer)
            await self.redis.lpush(queue, message)
            logger.debug(f"Pushed notification to queue: {queue}")
        except Exception as e:
            logger.error(f"Failed to push notification: {e}")

    # ── Generic ──────────────────────────────────────────────
    async def set_json(self, key: str, data: dict, ttl: int | None = None):
        if not self.redis:
            await self.connect()
        payload = json.dumps(data, default=default_json_serializer)
        if ttl:
            await self.redis.setex(key, ttl, payload)
        else:
            await self.redis.set(key, payload)

    async def get_json(self, key: str) -> dict | None:
        if not self.redis:
            await self.connect()
        raw = await self.redis.get(key)
        return json.loads(raw) if raw else None

    async def delete_key(self, key: str):
        if self.redis:
            await self.redis.delete(key)


redis_client = RedisClient()
