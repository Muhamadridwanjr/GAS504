"""
HTTP client for gas-smc-engine.
"""
from __future__ import annotations
from typing import Any
import httpx
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


class SMCClient:
    """Async HTTP client to gas-smc-engine."""

    def __init__(self):
        self.base_url = settings.SMC_ENGINE_URL.rstrip("/")
        self.timeout = settings.REQUEST_TIMEOUT

    async def detect(self, symbol: str, timeframe: str) -> dict[str, Any]:
        """Call SMC engine for a specific symbol."""
        url = f"{self.base_url}/detect"
        payload = {"symbol": symbol, "timeframe": timeframe}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            logger.error("SMC engine error for %s: %s", symbol, e)
            return {}
