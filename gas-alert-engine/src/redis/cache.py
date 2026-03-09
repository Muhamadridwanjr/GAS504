import json
from typing import Optional
from src.redis.client import redis_client
from src.config import settings
from src.lib.logger import logger
from src.lib.utils import default_json_serializer


class AlertCache:
    """Helpers for caching alert definitions and memberships in Redis."""

    PREFIX = settings.ALERT_CACHE_PREFIX  # "alert"

    # ── Alert definition cache ───────────────────────────────
    @staticmethod
    async def cache_alert(alert_id: str, alert_data: dict, ttl: int = 3600):
        """Cache a single alert definition."""
        key = f"{AlertCache.PREFIX}:{alert_id}"
        await redis_client.set_json(key, alert_data, ttl=ttl)

    @staticmethod
    async def get_cached_alert(alert_id: str) -> Optional[dict]:
        """Get a cached alert definition."""
        key = f"{AlertCache.PREFIX}:{alert_id}"
        return await redis_client.get_json(key)

    @staticmethod
    async def invalidate_alert(alert_id: str):
        """Remove a cached alert definition."""
        key = f"{AlertCache.PREFIX}:{alert_id}"
        await redis_client.delete_key(key)

    # ── Symbol:timeframe membership set ──────────────────────
    @staticmethod
    async def add_alert_to_set(symbol: str, timeframe: str, alert_id: str):
        """Add alert_id to the set of alerts for symbol:timeframe."""
        key = f"alerts:{symbol}:{timeframe}"
        if redis_client.redis:
            await redis_client.redis.sadd(key, alert_id)
            logger.debug(f"Added {alert_id} to {key}")

    @staticmethod
    async def remove_alert_from_set(symbol: str, timeframe: str, alert_id: str):
        key = f"alerts:{symbol}:{timeframe}"
        if redis_client.redis:
            await redis_client.redis.srem(key, alert_id)

    @staticmethod
    async def get_alert_ids_for(symbol: str, timeframe: str) -> set[str]:
        """Get all alert IDs for a symbol:timeframe combination."""
        key = f"alerts:{symbol}:{timeframe}"
        if redis_client.redis:
            return await redis_client.redis.smembers(key)
        return set()

    # ── Bulk rebuild cache ───────────────────────────────────
    @staticmethod
    async def rebuild_cache_for_alert(alert) -> None:
        """Rebuild cache entries when an alert is created/updated."""
        alert_data = {
            "id": str(alert.id),
            "user_id": str(alert.user_id),
            "name": alert.name,
            "symbol": alert.symbol,
            "timeframe": alert.timeframe or "ALL",
            "condition": alert.condition,
            "cooldown": alert.cooldown,
            "last_triggered": alert.last_triggered.isoformat() if alert.last_triggered else None,
            "metadata_info": alert.metadata_info,
        }
        await AlertCache.cache_alert(str(alert.id), alert_data)
        tf = alert.timeframe or "ALL"
        await AlertCache.add_alert_to_set(alert.symbol, tf, str(alert.id))


alert_cache = AlertCache()
