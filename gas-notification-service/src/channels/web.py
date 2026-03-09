import httpx
from src.config import settings
from src.lib.logger import logger
from src.core.exceptions import ChannelError

async def send_web_push(notification_data: dict):
    # Sends the notification securely to the internal websocket hub
    url = f"{settings.realtime_hub_url}/api/internal/broadcast"  # example endpoint
    
    # Normally the real-time hub might expect auth
    headers = {}
    if settings.internal_api_key:
        headers["X-API-Key"] = settings.internal_api_key

    # We broadcast to the specific user's channel in the real-time hub
    user_id = notification_data.get("user_id")
    payload = {
        "channel": f"user:{user_id}",
        "data": {
            "title": notification_data.get("title"),
            "message": notification_data.get("message"),
            "data": notification_data.get("data", {})
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            # We assume GAS realtime hub has an internal endpoint or we could publish directly to Redis.
            # However, for separation of concerns, POSTing or using Redis is fine. Let's use a dummy direct Redis publish for now:
            import redis.asyncio as redis
            import json
            
            redis_client = redis.from_url(settings.redis_url)
            channel_name = f"user:{user_id}"
            await redis_client.publish(
                "notification:user",
                json.dumps({
                    "channel": channel_name,
                    "data": payload["data"]
                })
            )
            await redis_client.close()
            logger.info(f"Published web notification to Redis for channel user:{user_id}")
    except Exception as e:
        logger.error(f"Failed to send web notification: {e}")
        raise ChannelError(f"Web push error: {e}")
