"""
Reader for external API data sources.
"""
from __future__ import annotations

from typing import Iterator

import httpx
import pandas as pd

from src.ingestor.base import BaseSource
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


class APIReader(BaseSource):
    """Reads OHLCV data from an external API with pagination."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or settings.SOURCE_API_URL
        self.api_key = api_key or settings.SOURCE_API_KEY

    def read(self, chunk_size: int = 100000) -> Iterator[pd.DataFrame]:
        """Fetch data page by page from the API."""
        if not self.base_url:
            logger.error("SOURCE_API_URL is not configured")
            return

        page = 1
        while True:
            logger.info("Fetching page %d from %s", page, self.base_url)
            try:
                resp = httpx.get(
                    self.base_url,
                    params={"page": page, "limit": chunk_size},
                    headers={"X-API-Key": self.api_key} if self.api_key else {},
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json().get("data", [])
                if not data:
                    break

                df = pd.DataFrame(data)
                df.columns = [c.lower().strip() for c in df.columns]
                if self.validate_schema(df):
                    yield df
                page += 1
            except httpx.HTTPError as exc:
                logger.error("API request failed: %s", exc)
                break

    def validate_schema(self, df: pd.DataFrame) -> bool:
        required = {"timestamp", "open", "high", "low", "close"}
        missing = required - set(df.columns)
        if missing:
            logger.warning("Missing columns from API: %s", missing)
            return False
        return True
