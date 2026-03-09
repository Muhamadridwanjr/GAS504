"""
Market data client for gas-rag-macro.
Fetches price data from gas-market-data-processor service.
"""
from __future__ import annotations

import httpx

from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


class MarketDataClient:
    """
    Async HTTP client to gas-market-data-processor.
    Gracefully returns None/empty on connectivity issues.
    """

    def __init__(self):
        self._base_url = settings.MARKET_DATA_SERVICE_URL
        self._api_key = settings.MARKET_DATA_API_KEY
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._client or self._client.is_closed:
            headers = {}
            if self._api_key:
                headers["X-API-Key"] = self._api_key
            self._client = httpx.AsyncClient(
                base_url=self._base_url, headers=headers, timeout=8.0
            )
        return self._client

    async def get_price_data(self, symbol: str) -> dict | None:
        """
        Fetch current OHLC price data for a symbol.

        Args:
            symbol: Trading symbol (e.g. 'XAUUSD').

        Returns:
            Dict with close, high, low, change_pct, or None on error.
        """
        try:
            client = await self._get_client()
            response = await client.get(f"/price/{symbol}")
            response.raise_for_status()
            data = response.json()
            return {
                "symbol": symbol,
                "close": data.get("close"),
                "high": data.get("high"),
                "low": data.get("low"),
                "change_pct": data.get("change_pct"),
                "timestamp": data.get("timestamp"),
            }
        except httpx.ConnectError:
            logger.warning("market_client.connect_error", symbol=symbol, url=self._base_url)
            return None
        except Exception as exc:
            logger.warning("market_client.error", symbol=symbol, error=str(exc))
            return None

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
