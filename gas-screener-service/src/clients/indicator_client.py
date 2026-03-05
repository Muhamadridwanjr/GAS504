"""
HTTP client for gas-indicator-engine.
"""
from __future__ import annotations
from typing import Any
import httpx
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


class IndicatorClient:
    """Async HTTP client to gas-indicator-engine."""

    def __init__(self):
        self.base_url = settings.INDICATOR_ENGINE_URL.rstrip("/")
        self.timeout = settings.REQUEST_TIMEOUT

    async def calculate(
        self, symbol: str, timeframe: str, indicators: list[dict]
    ) -> dict[str, Any]:
        """Call indicator engine for a specific symbol."""
        url = f"{self.base_url}/calculate"
        payload = {
            "symbol": symbol,
            "timeframe": timeframe,
            "indicators": indicators,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            logger.error("Indicator engine error for %s: %s", symbol, e)
            return {}
