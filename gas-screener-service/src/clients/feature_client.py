"""
HTTP client for gas-feature-engine (optional).
"""
from __future__ import annotations
from typing import Any
import httpx
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


class FeatureClient:
    def __init__(self):
        self.base_url = (settings.FEATURE_ENGINE_URL or "").rstrip("/")
        self.timeout = settings.REQUEST_TIMEOUT

    async def get_features(self, symbol: str, timeframe: str) -> dict[str, Any]:
        if not self.base_url:
            return {}
        url = f"{self.base_url}/features"
        payload = {"symbol": symbol, "timeframe": timeframe}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            logger.error("Feature engine error for %s: %s", symbol, e)
            return {}
