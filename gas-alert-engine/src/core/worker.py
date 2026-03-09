"""
Market Data Worker for gas-alert-engine.

Subscribes to Redis pub/sub channel `market:data`.
On each incoming message, evaluates all active alerts for the symbol/timeframe.
If an alert is triggered, pushes a notification task to the Redis queue.
"""

import json
import asyncio
from datetime import datetime, timezone
from src.redis.client import redis_client
from src.redis.cache import alert_cache
from src.core.evaluator import evaluate_condition
from src.config import settings
from src.lib.logger import logger
from src.db.database import AsyncSessionLocal
from src.db.repositories.alert_repo import AlertRepository


async def process_market_data(message_data: str) -> None:
    """Process a single market data message and evaluate alerts."""
    try:
        data = json.loads(message_data)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in market data message")
        return

    symbol = data.get("symbol", "")
    timeframe = data.get("timeframe", "ALL")

    if not symbol:
        return

    # Get alert IDs from Redis set
    alert_ids = await alert_cache.get_alert_ids_for(symbol, timeframe)

    # Also check "ALL" timeframe alerts
    if timeframe != "ALL":
        all_ids = await alert_cache.get_alert_ids_for(symbol, "ALL")
        alert_ids = alert_ids | all_ids

    if not alert_ids:
        return

    logger.debug(f"Evaluating {len(alert_ids)} alerts for {symbol}:{timeframe}")

    for alert_id in alert_ids:
        try:
            await evaluate_single_alert(alert_id, data)
        except Exception as e:
            logger.error(f"Error evaluating alert {alert_id}: {e}")


async def evaluate_single_alert(alert_id: str, market_data: dict) -> None:
    """Evaluate a single alert against market data."""
    # Get alert definition from cache
    alert_def = await alert_cache.get_cached_alert(alert_id)

    if not alert_def:
        # Try to load from DB and cache it
        async with AsyncSessionLocal() as session:
            repo = AlertRepository(session)
            from uuid import UUID
            alert_obj = await repo.get_by_id(UUID(alert_id))
            if not alert_obj or not alert_obj.active:
                return
            await alert_cache.rebuild_cache_for_alert(alert_obj)
            alert_def = await alert_cache.get_cached_alert(alert_id)
            if not alert_def:
                return

    # Check cooldown
    last_triggered = alert_def.get("last_triggered")
    cooldown = alert_def.get("cooldown", 0)
    if last_triggered and cooldown > 0:
        try:
            lt = datetime.fromisoformat(last_triggered)
            elapsed = (datetime.now(timezone.utc) - lt).total_seconds()
            if elapsed < cooldown:
                logger.debug(f"Alert {alert_id} in cooldown ({elapsed:.0f}s / {cooldown}s)")
                return
        except (ValueError, TypeError):
            pass

    # Evaluate condition
    condition = alert_def.get("condition", {})
    triggered = evaluate_condition(condition, market_data)

    if triggered:
        logger.info(f"🔔 Alert {alert_id} TRIGGERED for {market_data.get('symbol')}")

        # Record trigger in DB
        async with AsyncSessionLocal() as session:
            repo = AlertRepository(session)
            from uuid import UUID
            trigger_snapshot = {
                "symbol": market_data.get("symbol"),
                "timeframe": market_data.get("timeframe"),
                "close": market_data.get("close"),
                "triggered_at": datetime.now(timezone.utc).isoformat(),
            }
            await repo.record_trigger(UUID(alert_id), trigger_snapshot)

        # Update cache with new last_triggered
        alert_def["last_triggered"] = datetime.now(timezone.utc).isoformat()
        await alert_cache.cache_alert(alert_id, alert_def)

        # Push notification to queue
        notification = {
            "type": "alert_triggered",
            "alert_id": alert_id,
            "user_id": alert_def.get("user_id"),
            "alert_name": alert_def.get("name", "Unnamed Alert"),
            "symbol": market_data.get("symbol"),
            "timeframe": market_data.get("timeframe"),
            "condition": condition,
            "trigger_data": {
                "close": market_data.get("close"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        await redis_client.push_notification(settings.NOTIFICATION_QUEUE, notification)


async def start_worker() -> None:
    """Start the market data worker (runs in background)."""
    logger.info(f"Starting market data worker on channel: {settings.MARKET_DATA_CHANNEL}")

    try:
        pubsub = await redis_client.subscribe(settings.MARKET_DATA_CHANNEL)

        async for message in pubsub.listen():
            if message["type"] == "message":
                await process_market_data(message["data"])

    except asyncio.CancelledError:
        logger.info("Worker cancelled, shutting down...")
    except Exception as e:
        logger.error(f"Worker error: {e}")
        # Retry after delay
        await asyncio.sleep(5)
        await start_worker()
