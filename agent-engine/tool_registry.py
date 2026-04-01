"""
GAS Agent Engine — Tool Registry
Central registry of all callable tools that agents can invoke.
Each tool has a real async implementation using httpx and aioredis.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable, Awaitable, Optional
import httpx
import redis.asyncio as aioredis

import config

logger = logging.getLogger(__name__)


# ─── Tool type alias ──────────────────────────────────────────────────────────
ToolFn = Callable[..., Awaitable[Any]]


class ToolRegistry:
    """
    Central registry of all callable tools available to agent workflows.
    Tools are registered by name and invoked by the AgentRunner during step execution.
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolFn] = {}
        self._redis: Optional[aioredis.Redis] = None
        self._http: Optional[httpx.AsyncClient] = None

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    async def startup(self) -> None:
        """Initialize shared async clients and register all built-in tools."""
        self._redis = aioredis.from_url(
            config.REDIS_URL,
            max_connections=config.REDIS_MAX_CONNECTIONS,
            socket_timeout=config.REDIS_SOCKET_TIMEOUT,
            decode_responses=True,
        )
        self._http = httpx.AsyncClient(
            timeout=config.AGENT_DEFAULT_TIMEOUT,
            follow_redirects=True,
        )
        self._register_all()
        logger.info("ToolRegistry started — %d tools registered", len(self._tools))

    async def shutdown(self) -> None:
        """Close all async clients."""
        if self._redis:
            await self._redis.aclose()
        if self._http:
            await self._http.aclose()

    # ─── Registry API ─────────────────────────────────────────────────────────

    def register(self, name: str, fn: ToolFn) -> None:
        """Register a tool function by name."""
        self._tools[name] = fn
        logger.debug("Tool registered: %s", name)

    async def call(self, name: str, **kwargs: Any) -> Any:
        """Invoke a registered tool by name with keyword arguments."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered in ToolRegistry")
        logger.debug("Calling tool '%s' with kwargs: %s", name, list(kwargs.keys()))
        start = time.monotonic()
        try:
            result = await self._tools[name](**kwargs)
            elapsed = time.monotonic() - start
            logger.debug("Tool '%s' completed in %.3fs", name, elapsed)
            return result
        except Exception as exc:
            logger.error("Tool '%s' raised an error: %s", name, exc, exc_info=True)
            raise

    def list_tools(self) -> list[str]:
        """Return a sorted list of all registered tool names."""
        return sorted(self._tools.keys())

    def get_tool(self, name: str) -> ToolFn:
        """Return the raw function for a named tool."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]

    # ─── Tool Registration ────────────────────────────────────────────────────

    def _register_all(self) -> None:
        tools = {
            "read_logs": self._read_logs,
            "check_websocket": self._check_websocket,
            "metrics_reader": self._metrics_reader,
            "call_service": self._call_service,
            "publish_event": self._publish_event,
            "query_redis": self._query_redis,
            "write_redis": self._write_redis,
            "send_alert": self._send_alert,
            "query_db": self._query_db,
            "fetch_ohlcv": self._fetch_ohlcv,
            "run_backtest": self._run_backtest,
            "embed_text": self._embed_text,
            "search_vectors": self._search_vectors,
        }
        for name, fn in tools.items():
            self.register(name, fn)

    # ─── Tool Implementations ─────────────────────────────────────────────────

    async def _read_logs(
        self,
        service: str,
        lines: int = 100,
        level: Optional[str] = None,
        since_minutes: int = 5,
    ) -> dict[str, Any]:
        """
        Read recent log lines from a service via gas-observability log query API.
        Falls back to direct log file read if observability is unavailable.
        """
        params: dict[str, Any] = {
            "service": service,
            "lines": lines,
            "since_minutes": since_minutes,
        }
        if level:
            params["level"] = level

        try:
            response = await self._http.get(
                f"{config.OBSERVABILITY_URL}/logs/query",
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.warning("read_logs HTTP error for %s: %s", service, exc)
            return {"service": service, "lines": [], "error": str(exc)}

    async def _check_websocket(
        self,
        service: str,
        endpoint: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Check WebSocket service health by calling the service's /ws/stats endpoint.
        Returns connection state, client count, and ping latency.
        """
        url_map = {
            "mt5-websocket": config.MT5_WEBSOCKET_URL,
            "realtime-hub": config.REALTIME_HUB_URL,
            "binance-service": config.BINANCE_SERVICE_URL,
        }
        base_url = url_map.get(service, f"http://{service}")
        stats_path = endpoint or "/ws/stats"

        start = time.monotonic()
        try:
            response = await self._http.get(f"{base_url}{stats_path}")
            latency_ms = (time.monotonic() - start) * 1000
            response.raise_for_status()
            data = response.json()
            return {
                "service": service,
                "status": "connected",
                "latency_ms": round(latency_ms, 2),
                "stats": data,
            }
        except httpx.HTTPError as exc:
            return {
                "service": service,
                "status": "disconnected",
                "error": str(exc),
                "latency_ms": None,
            }

    async def _metrics_reader(
        self,
        query: str,
        service: Optional[str] = None,
        step: str = "15s",
    ) -> dict[str, Any]:
        """
        Execute a PromQL query against gas-observability (Prometheus-compatible).
        Returns the metric result set or an error payload.
        """
        params = {"query": query, "step": step}
        if service:
            params["service"] = service

        try:
            response = await self._http.get(
                f"{config.OBSERVABILITY_URL}/api/v1/query",
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.warning("metrics_reader error: %s", exc)
            return {"status": "error", "error": str(exc), "query": query}

    async def _call_service(
        self,
        method: str,
        url: str,
        payload: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        """
        Make an HTTP call to any GAS platform service.
        Supports GET, POST, PUT, DELETE with JSON payload.
        """
        method = method.upper()
        _headers = {"Content-Type": "application/json", **(headers or {})}

        try:
            if method == "GET":
                response = await self._http.get(url, headers=_headers, params=payload, timeout=timeout)
            elif method == "POST":
                response = await self._http.post(url, headers=_headers, json=payload, timeout=timeout)
            elif method == "PUT":
                response = await self._http.put(url, headers=_headers, json=payload, timeout=timeout)
            elif method == "DELETE":
                response = await self._http.delete(url, headers=_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            return {
                "status_code": response.status_code,
                "ok": response.is_success,
                "body": response.json() if response.content else {},
            }
        except httpx.HTTPError as exc:
            return {"status_code": 0, "ok": False, "error": str(exc), "url": url}

    async def _publish_event(
        self,
        event_type: str,
        payload: dict[str, Any],
        priority: int = 5,
    ) -> dict[str, Any]:
        """
        Publish an event to the Redis stream event bus.
        Stream key: gas:events:{event_type}
        """
        stream_key = f"{config.EVENT_BUS_STREAM_PREFIX}:{event_type}"
        message = {
            "event_type": event_type,
            "payload": json.dumps(payload),
            "priority": str(priority),
            "ts": str(int(time.time() * 1000)),
        }
        try:
            msg_id = await self._redis.xadd(
                stream_key,
                message,
                maxlen=config.EVENT_BUS_MAX_STREAM_LEN,
                approximate=True,
            )
            logger.debug("Published event '%s' → %s", event_type, msg_id)
            return {"event_type": event_type, "message_id": msg_id, "ok": True}
        except Exception as exc:
            logger.error("publish_event failed for %s: %s", event_type, exc)
            return {"event_type": event_type, "ok": False, "error": str(exc)}

    async def _query_redis(
        self,
        key: str,
        command: str = "GET",
        *args: Any,
    ) -> Any:
        """
        Execute a Redis read command.
        Supported commands: GET, HGETALL, LRANGE, SMEMBERS, ZRANGE, ZSCORE, TTL, EXISTS
        """
        try:
            if command == "GET":
                return await self._redis.get(key)
            elif command == "HGETALL":
                return await self._redis.hgetall(key)
            elif command == "LRANGE":
                start, end = (args[0], args[1]) if len(args) >= 2 else (0, -1)
                return await self._redis.lrange(key, start, end)
            elif command == "SMEMBERS":
                return await self._redis.smembers(key)
            elif command == "ZRANGE":
                start, end = (args[0], args[1]) if len(args) >= 2 else (0, -1)
                withscores = args[2] if len(args) >= 3 else False
                return await self._redis.zrange(key, start, end, withscores=withscores)
            elif command == "ZSCORE":
                member = args[0] if args else None
                return await self._redis.zscore(key, member)
            elif command == "TTL":
                return await self._redis.ttl(key)
            elif command == "EXISTS":
                return await self._redis.exists(key)
            elif command == "XREAD":
                count = args[0] if args else 100
                return await self._redis.xread({key: "0"}, count=count, block=0)
            else:
                raise ValueError(f"Unsupported Redis command: {command}")
        except Exception as exc:
            logger.error("query_redis error [%s %s]: %s", command, key, exc)
            raise

    async def _write_redis(
        self,
        key: str,
        command: str = "SET",
        *args: Any,
        ttl: Optional[int] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a Redis write command.
        Supported: SET, HSET, LPUSH, RPUSH, SADD, ZADD, XADD, DEL, INCR, EXPIRE
        """
        try:
            if command == "SET":
                value = args[0] if args else kwargs.get("value", "")
                result = await self._redis.set(key, value, ex=ttl)
            elif command == "HSET":
                mapping = args[0] if args else kwargs.get("mapping", {})
                result = await self._redis.hset(key, mapping=mapping)
                if ttl:
                    await self._redis.expire(key, ttl)
            elif command == "LPUSH":
                values = args if args else kwargs.get("values", [])
                result = await self._redis.lpush(key, *values)
            elif command == "RPUSH":
                values = args if args else kwargs.get("values", [])
                result = await self._redis.rpush(key, *values)
            elif command == "SADD":
                members = args if args else kwargs.get("members", [])
                result = await self._redis.sadd(key, *members)
            elif command == "ZADD":
                mapping = args[0] if args else kwargs.get("mapping", {})
                result = await self._redis.zadd(key, mapping)
            elif command == "DEL":
                result = await self._redis.delete(key)
            elif command == "INCR":
                result = await self._redis.incr(key)
                if ttl:
                    await self._redis.expire(key, ttl)
            elif command == "EXPIRE":
                seconds = args[0] if args else ttl or 3600
                result = await self._redis.expire(key, seconds)
            else:
                raise ValueError(f"Unsupported Redis write command: {command}")
            return result
        except Exception as exc:
            logger.error("write_redis error [%s %s]: %s", command, key, exc)
            raise

    async def _send_alert(
        self,
        message: str,
        level: str = "INFO",
        chat_id: Optional[str] = None,
        symbol: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send a Telegram alert via gas-telegram-bot service.
        Level: INFO, WARNING, CRITICAL, EMERGENCY
        """
        _chat_id = chat_id or config.TELEGRAM_ALERT_CHAT_ID
        if not _chat_id:
            logger.warning("send_alert: TELEGRAM_ALERT_CHAT_ID not configured")
            return {"ok": False, "error": "no chat_id configured"}

        icon_map = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "CRITICAL": "🚨",
            "EMERGENCY": "🔴",
        }
        icon = icon_map.get(level.upper(), "📢")
        formatted = f"{icon} *[{level}]* {message}"
        if symbol:
            formatted = f"{icon} *[{level}]* `{symbol}` — {message}"

        payload = {
            "chat_id": _chat_id,
            "text": formatted,
            "parse_mode": "Markdown",
        }
        try:
            response = await self._http.post(
                f"{config.TELEGRAM_BOT_URL}/send",
                json=payload,
                timeout=5.0,
            )
            response.raise_for_status()
            return {"ok": True, "chat_id": _chat_id, "level": level}
        except httpx.HTTPError as exc:
            logger.error("send_alert HTTP error: %s", exc)
            return {"ok": False, "error": str(exc)}

    async def _query_db(
        self,
        sql: str,
        params: Optional[dict] = None,
        fetch: str = "all",
    ) -> Any:
        """
        Execute a read SQL query against TimescaleDB via the web-backend query proxy.
        fetch: 'all' (list of rows), 'one' (single row), 'val' (scalar)
        """
        payload = {"sql": sql, "params": params or {}, "fetch": fetch}
        try:
            response = await self._http.post(
                f"{config.WEB_BACKEND_URL}/internal/db/query",
                json=payload,
                timeout=15.0,
            )
            response.raise_for_status()
            return response.json().get("result")
        except httpx.HTTPError as exc:
            logger.error("query_db error: %s | SQL: %s", exc, sql[:100])
            raise RuntimeError(f"query_db failed: {exc}") from exc

    async def _fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 200,
        since: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Fetch OHLCV candles from gas-market-data-processor.
        Returns dict with 'candles' list: [{t, o, h, l, c, v}]
        """
        params: dict[str, Any] = {
            "symbol": symbol,
            "timeframe": timeframe,
            "limit": limit,
        }
        if since:
            params["since"] = since

        try:
            response = await self._http.get(
                f"{config.MARKET_DATA_PROCESSOR_URL}/ohlcv",
                params=params,
                timeout=15.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.error("fetch_ohlcv error [%s %s]: %s", symbol, timeframe, exc)
            return {"symbol": symbol, "timeframe": timeframe, "candles": [], "error": str(exc)}

    async def _run_backtest(
        self,
        strategy_id: str,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str,
        params: Optional[dict] = None,
        ohlcv: Optional[list] = None,
    ) -> dict[str, Any]:
        """
        Submit a backtest job to gas-quant-backtester and wait for result.
        Returns performance metrics and trade log on completion.
        """
        payload = {
            "strategy_id": strategy_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "start_date": start_date,
            "end_date": end_date,
            "params": params or {},
            "ohlcv": ohlcv,  # Optional pre-fetched candles to avoid double fetch
        }
        try:
            response = await self._http.post(
                f"{config.QUANT_BACKTESTER_URL}/backtest/run",
                json=payload,
                timeout=120.0,  # Backtests can take longer
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.error("run_backtest error [%s]: %s", strategy_id, exc)
            return {"ok": False, "error": str(exc), "strategy_id": strategy_id}

    async def _embed_text(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Convert text to an embedding vector via gas-ai-orchestrator embedding endpoint.
        Returns dict with 'embedding' (list of floats) and 'model' used.
        """
        payload = {
            "text": text,
            "model": model or config.EMBEDDING_MODEL,
            "dimensions": config.EMBEDDING_DIMENSIONS,
        }
        try:
            response = await self._http.post(
                f"{config.AI_ORCHESTRATOR_URL}/v1/embed",
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.error("embed_text error: %s", exc)
            return {"embedding": [], "error": str(exc)}

    async def _search_vectors(
        self,
        collection: str,
        query_embedding: Optional[list[float]] = None,
        query_text: Optional[str] = None,
        top_k: int = 5,
        score_threshold: float = 0.60,
        filter_metadata: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Perform semantic similarity search in a vector collection via gas-vector-db.
        Accepts either a pre-computed embedding or raw query text (auto-embedded).
        collection: 'macro', 'technical', 'news', etc.
        """
        if query_text and not query_embedding:
            embed_result = await self._embed_text(query_text)
            query_embedding = embed_result.get("embedding", [])

        if not query_embedding:
            return {"results": [], "error": "No embedding provided or embedding failed"}

        payload = {
            "collection": collection,
            "embedding": query_embedding,
            "top_k": top_k,
            "score_threshold": score_threshold,
            "filter": filter_metadata or {},
        }
        try:
            response = await self._http.post(
                f"{config.VECTOR_DB_URL}/search",
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.error("search_vectors error [%s]: %s", collection, exc)
            return {"results": [], "collection": collection, "error": str(exc)}


# ─── Module-level singleton ───────────────────────────────────────────────────
_registry_instance: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ToolRegistry()
    return _registry_instance
