"""World Bank API client."""
from __future__ import annotations
import httpx
from src.ingestion.base import BaseSource
from src.lib.logger import get_logger

logger = get_logger(__name__)

class WorldBankClient(BaseSource):
    BASE_URL = "https://api.worldbank.org/v2"

    async def fetch(self, indicator: str, from_time: int = 0, to_time: int = 0) -> list[dict]:
        url = f"{self.BASE_URL}/country/all/indicator/{indicator}"
        params = {"format": "json", "per_page": 1000}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                if len(data) < 2: return []
                return [{"time": d.get("date",""), "value": float(d.get("value",0))} for d in data[1] if d.get("value") is not None]
        except Exception as e:
            logger.error("World Bank fetch error: %s", e)
            return []
