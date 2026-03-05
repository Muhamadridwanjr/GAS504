"""
Data validation logic for ingested data.
"""
from __future__ import annotations

import pandas as pd

from src.lib.logger import get_logger

logger = get_logger(__name__)


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean OHLCV data.

    - Drop rows with null timestamp, open, high, low, close.
    - Ensure high >= low.
    - Convert timestamp to UNIX int.
    """
    before = len(df)

    # Drop nulls on mandatory columns
    mandatory = ["timestamp", "open", "high", "low", "close"]
    df = df.dropna(subset=mandatory)

    # Ensure high >= low
    df = df[df["high"] >= df["low"]]

    # Convert timestamp to UNIX int
    if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["unix_time"] = df["timestamp"].astype("int64") // 10**9
    else:
        df["unix_time"] = pd.to_numeric(df["timestamp"], errors="coerce").astype("Int64")
        df = df.dropna(subset=["unix_time"])

    # Add partition columns
    if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["year"] = df["timestamp"].dt.year
        df["month"] = df["timestamp"].dt.month
    else:
        ts = pd.to_datetime(df["timestamp"], errors="coerce")
        df["year"] = ts.dt.year
        df["month"] = ts.dt.month

    after = len(df)
    if before != after:
        logger.info("Validation dropped %d rows (%d → %d)", before - after, before, after)

    return df
