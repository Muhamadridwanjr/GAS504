"""FRED API client for economic data."""
from __future__ import annotations
import httpx
from src.ingestion.base import BaseSource
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

class FREDClient(BaseSource):
    BASE_URL = "https://api.stlouisfed.org/fred"

    async def fetch(self, indicator: str, from_time: int = 0, to_time: int = 0) -> list[dict]:
        if not settings.FRED_API_KEY:
            logger.warning("FRED_API_KEY not set")
            return []
        url = f"{self.BASE_URL}/series/observations"
        params = {"series_id": indicator, "api_key": settings.FRED_API_KEY, "file_type": "json"}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                obs = resp.json().get("observations", [])
                return [{"time": o.get("date",""), "value": float(o.get("value",0))} for o in obs if o.get("value",".")!="."]
        except Exception as e:
            logger.error("FRED fetch error: %s", e)
            return []
