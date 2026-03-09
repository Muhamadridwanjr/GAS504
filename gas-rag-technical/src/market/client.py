"""
Market data client – fetches current OHLC and indicators
from gas-market-data-processor service.
"""
from __future__ import annotations
from typing import Any
import httpx
from src.config import settings
from src.core.exceptions import MarketDataError
from src.lib.logger import get_logger

logger = get_logger(__name__)

TIMEOUT = 10.0  # seconds


class MarketDataClient:
    """HTTP client for gas-market-data-processor."""

    def __init__(self) -> None:
        self._base_url = settings.MARKET_DATA_SERVICE_URL.rstrip("/")
        headers: dict[str, str] = {}
        if settings.MARKET_DATA_API_KEY:
            headers["X-API-Key"] = settings.MARKET_DATA_API_KEY
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=TIMEOUT,
        )

    async def get_ohlc(self, symbol: str, timeframe: str) -> dict[str, Any]:
        """Fetch latest OHLC candles for symbol/timeframe."""
        try:
            resp = await self._client.get(
                "/ohlc",
                params={"symbol": symbol, "timeframe": timeframe, "limit": 1},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            logger.warning("Market OHLC fetch failed: %s", exc)
            return {}

    async def get_current_price(self, symbol: str) -> dict[str, Any]:
        """Fetch current bid/ask for symbol."""
        try:
            resp = await self._client.get("/price", params={"symbol": symbol})
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            logger.warning("Market price fetch failed: %s", exc)
            return {}

    async def get_market_context(
        self, symbol: str, timeframe: str
    ) -> dict[str, Any]:
        """Aggregate OHLC + current price into a single context dict."""
        try:
            ohlc = await self.get_ohlc(symbol, timeframe)
            price = await self.get_current_price(symbol)
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "ohlc": ohlc,
                "current": price,
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Market context collection failed: %s", exc)
            return {"symbol": symbol, "timeframe": timeframe, "error": str(exc)}

    async def close(self) -> None:
        await self._client.aclose()
