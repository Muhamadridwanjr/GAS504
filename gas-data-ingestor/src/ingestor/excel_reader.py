"""
Reader for Excel/CSV data sources.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pandas as pd

from src.ingestor.base import BaseSource
from src.lib.logger import get_logger

logger = get_logger(__name__)

REQUIRED_COLUMNS = {"timestamp", "open", "high", "low", "close"}


class ExcelCSVReader(BaseSource):
    """Reads data from Excel (.xlsx) or CSV files in chunks."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Source file not found: {self.file_path}")
        self.extension = self.file_path.suffix.lower()

    def read(self, chunk_size: int = 100000) -> Iterator[pd.DataFrame]:
        """Read the file in chunks."""
        logger.info("Reading file %s in chunks of %d", self.file_path, chunk_size)

        if self.extension in (".xlsx", ".xls"):
            # Excel files are read entirely then chunked
            df = pd.read_excel(self.file_path)
            df.columns = [c.lower().strip() for c in df.columns]
            for start in range(0, len(df), chunk_size):
                chunk = df.iloc[start : start + chunk_size].copy()
                if self.validate_schema(chunk):
                    yield self._normalize(chunk)
        else:
            # CSV supports native chunked reading
            for chunk in pd.read_csv(self.file_path, chunksize=chunk_size):
                chunk.columns = [c.lower().strip() for c in chunk.columns]
                if self.validate_schema(chunk):
                    yield self._normalize(chunk)

    def validate_schema(self, df: pd.DataFrame) -> bool:
        """Check that required OHLC columns exist."""
        cols = set(df.columns)
        missing = REQUIRED_COLUMNS - cols
        if missing:
            logger.warning("Missing columns: %s — skipping chunk", missing)
            return False
        return True

    @staticmethod
    def _normalize(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column types."""
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        for col in ("open", "high", "low", "close"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        if "volume" in df.columns:
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype(int)
        return df
