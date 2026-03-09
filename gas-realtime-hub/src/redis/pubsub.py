import redis.asyncio as redis
import asyncio
import json
from src.config import settings
from src.lib.logger import logger
from src.server.connection_manager import manager

class RedisSubscriber:
    def __init__(self):
        self.redis: redis.Redis = None
        self.pubsub = None
        self.task = None

    async def connect(self):
        try:
            self.redis = redis.from_url(settings.redis_url)
            self.pubsub = self.redis.pubsub()
            # Subscribe to pattern matching channels
            await self.pubsub.psubscribe("market:*", "ohlc:*", "signal:*", "notification:*", "broadcast")
            logger.info(f"Connected to Redis & subscribed to channels at {settings.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")

    async def listen(self):
        if not self.pubsub:
            return
            
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "pmessage" or message["type"] == "message":
                    channel = message["channel"].decode("utf-8")
                    data_str = message["data"].decode("utf-8")
                    
                    try:
                        data = json.loads(data_str)
                        # Expecting format: {"channel": "...", "data": {...}}
                        target_channel = data.get("channel", channel)
                        
                        ws_message = {
                            "type": "data",
                            "channel": target_channel,
                            "data": data.get("data", data)
                        }
                        
                        await manager.broadcast_to_channel(target_channel, ws_message)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse message from Redis channel {channel}: {data_str}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Redis listener logic: {e}")

    async def start(self):
        await self.connect()
        self.task = asyncio.create_task(self.listen())

    async def stop(self):
        if self.task:
            self.task.cancel()
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()
            
redis_subscriber = RedisSubscriber()
