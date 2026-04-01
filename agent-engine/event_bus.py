"""
GAS Agent Engine — Event Bus
Pub/sub event system built on Redis Streams.
Agents publish events and subscribe to event types via consumer groups.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Callable, Awaitable, Optional

import redis.asyncio as aioredis

import config

logger = logging.getLogger(__name__)

# Handler type: async function receiving (event_type, payload) → None
EventHandler = Callable[[str, dict[str, Any]], Awaitable[None]]


class EventBus:
    """
    Redis Streams-based pub/sub event bus for the GAS Agent Engine.

    Each event type gets its own stream key: gas:events:{event_type}
    Consumers join a named consumer group to enable at-least-once delivery
    and automatic load balancing when multiple instances run.
    """

    def __init__(
        self,
        redis_url: str = config.REDIS_URL,
        stream_prefix: str = config.EVENT_BUS_STREAM_PREFIX,
        consumer_group: str = config.EVENT_BUS_CONSUMER_GROUP,
        block_ms: int = config.EVENT_BUS_BLOCK_MS,
        max_stream_len: int = config.EVENT_BUS_MAX_STREAM_LEN,
    ) -> None:
        self._redis_url = redis_url
        self._stream_prefix = stream_prefix
        self._consumer_group = consumer_group
        self._block_ms = block_ms
        self._max_stream_len = max_stream_len

        self._redis: Optional[aioredis.Redis] = None
        self._handlers: dict[str, list[EventHandler]] = {}  # event_type → handlers
        self._consumer_id = f"consumer-{int(time.time())}"
        self._running = False
        self._consume_task: Optional[asyncio.Task] = None

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    async def connect(self) -> None:
        """Establish Redis connection and ensure consumer groups exist."""
        self._redis = aioredis.from_url(
            self._redis_url,
            max_connections=10,
            decode_responses=True,
        )
        await self._redis.ping()
        logger.info("EventBus connected to Redis — consumer: %s", self._consumer_id)

    async def disconnect(self) -> None:
        """Stop consuming and close Redis connection."""
        await self.stop()
        if self._redis:
            await self._redis.aclose()
        logger.info("EventBus disconnected")

    # ─── Publish ──────────────────────────────────────────────────────────────

    async def publish(
        self,
        event_type: str,
        payload: dict[str, Any],
        priority: int = 5,
    ) -> str:
        """
        Publish an event to the Redis stream for the given event_type.
        Returns the stream message ID assigned by Redis.
        """
        if not self._redis:
            raise RuntimeError("EventBus not connected — call connect() first")

        stream_key = f"{self._stream_prefix}:{event_type}"
        message: dict[str, str] = {
            "event_type": event_type,
            "payload": json.dumps(payload, default=str),
            "priority": str(priority),
            "publisher": self._consumer_id,
            "ts": str(int(time.time() * 1000)),
        }
        msg_id = await self._redis.xadd(
            stream_key,
            message,
            maxlen=self._max_stream_len,
            approximate=True,
        )
        logger.debug("Published event '%s' id=%s", event_type, msg_id)
        return msg_id

    async def publish_many(
        self,
        events: list[tuple[str, dict[str, Any]]],
        priority: int = 5,
    ) -> list[str]:
        """Publish multiple events in sequence. Returns list of message IDs."""
        ids = []
        for event_type, payload in events:
            msg_id = await self.publish(event_type, payload, priority)
            ids.append(msg_id)
        return ids

    # ─── Subscribe ────────────────────────────────────────────────────────────

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Register a handler for a specific event type.
        Multiple handlers can be registered for the same event type.
        Handler signature: async def handler(event_type: str, payload: dict) -> None
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug("Subscribed handler '%s' to event '%s'", handler.__name__, event_type)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove a specific handler from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h is not handler
            ]

    # ─── Consume ──────────────────────────────────────────────────────────────

    async def start_consuming(self) -> None:
        """
        Start the background consume loop.
        Creates consumer groups for all subscribed event types and begins reading.
        """
        if self._running:
            logger.warning("EventBus consume loop already running")
            return

        self._running = True
        await self._ensure_consumer_groups()
        self._consume_task = asyncio.create_task(self._consume_loop())
        logger.info(
            "EventBus consume loop started — watching %d event types",
            len(self._handlers),
        )

    async def stop(self) -> None:
        """Stop the consume loop gracefully."""
        self._running = False
        if self._consume_task and not self._consume_task.done():
            self._consume_task.cancel()
            try:
                await self._consume_task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus consume loop stopped")

    async def _ensure_consumer_groups(self) -> None:
        """Create consumer groups for all registered event type streams."""
        for event_type in self._handlers:
            stream_key = f"{self._stream_prefix}:{event_type}"
            try:
                # Ensure the stream exists with a sentinel entry
                await self._redis.xadd(stream_key, {"_init": "1"}, maxlen=1)
                await self._redis.xgroup_create(
                    stream_key,
                    self._consumer_group,
                    id="$",   # Start consuming new messages only
                    mkstream=True,
                )
                logger.debug("Created consumer group for stream: %s", stream_key)
            except aioredis.ResponseError as exc:
                if "BUSYGROUP" in str(exc):
                    pass  # Group already exists — that is fine
                else:
                    logger.error("Failed to create consumer group for %s: %s", stream_key, exc)

    async def _consume_loop(self) -> None:
        """Main consume loop: reads from all subscribed streams via XREADGROUP."""
        streams = {
            f"{self._stream_prefix}:{et}": ">"
            for et in self._handlers
        }
        if not streams:
            logger.warning("EventBus consume loop started but no subscriptions registered")
            return

        while self._running:
            try:
                results = await self._redis.xreadgroup(
                    groupname=self._consumer_group,
                    consumername=self._consumer_id,
                    streams=streams,
                    count=10,
                    block=self._block_ms,
                )
                if not results:
                    continue

                for stream_key, messages in results:
                    event_type = stream_key.split(":")[-1]
                    for msg_id, fields in messages:
                        await self._dispatch(event_type, msg_id, fields)

            except asyncio.CancelledError:
                break
            except aioredis.ConnectionError as exc:
                logger.error("EventBus Redis connection lost: %s — retrying in 5s", exc)
                await asyncio.sleep(5)
            except Exception as exc:
                logger.error("EventBus consume loop error: %s", exc, exc_info=True)
                await asyncio.sleep(1)

    async def _dispatch(
        self,
        event_type: str,
        msg_id: str,
        fields: dict[str, str],
    ) -> None:
        """Dispatch a received message to all registered handlers for its event type."""
        try:
            raw_payload = fields.get("payload", "{}")
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            logger.warning("EventBus: failed to parse payload for event %s msg %s", event_type, msg_id)
            payload = {}

        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_type, payload)
            except Exception as exc:
                logger.error(
                    "EventBus handler '%s' raised error for event '%s': %s",
                    handler.__name__, event_type, exc,
                    exc_info=True,
                )

        # ACK the message after all handlers have run
        stream_key = f"{self._stream_prefix}:{event_type}"
        try:
            await self._redis.xack(stream_key, self._consumer_group, msg_id)
        except Exception as exc:
            logger.warning("EventBus: failed to ACK msg %s: %s", msg_id, exc)

    # ─── Utilities ────────────────────────────────────────────────────────────

    async def get_stream_info(self, event_type: str) -> dict[str, Any]:
        """Return info about a stream: length, groups, last message."""
        stream_key = f"{self._stream_prefix}:{event_type}"
        try:
            info = await self._redis.xinfo_stream(stream_key)
            return {
                "stream": stream_key,
                "length": info.get("length", 0),
                "first_entry": info.get("first-entry"),
                "last_entry": info.get("last-entry"),
            }
        except Exception as exc:
            return {"stream": stream_key, "error": str(exc)}

    async def pending_count(self, event_type: str) -> int:
        """Return the number of unacknowledged (pending) messages for this consumer group."""
        stream_key = f"{self._stream_prefix}:{event_type}"
        try:
            pending = await self._redis.xpending(stream_key, self._consumer_group)
            return pending.get("pending", 0) if isinstance(pending, dict) else 0
        except Exception:
            return 0

    @property
    def subscribed_events(self) -> list[str]:
        """List of event types this bus is currently subscribed to."""
        return list(self._handlers.keys())


# ─── Module-level singleton ───────────────────────────────────────────────────
_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = EventBus()
    return _bus_instance
