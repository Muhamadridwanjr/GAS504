"""Utility helpers for gas-rag-technical."""
import time
import hashlib
import json
from typing import Any


def now_ts() -> int:
    """Return current UTC timestamp as integer."""
    return int(time.time())


def make_analysis_id(symbol: str, timeframe: str, ts: int | None = None) -> str:
    """Generate a unique analysis ID."""
    ts = ts or now_ts()
    return f"analysis_{symbol}_{timeframe}_{ts}"


def hash_query(query: str, symbol: str, timeframe: str) -> str:
    """Create a cache key for a given query."""
    payload = json.dumps({"q": query, "s": symbol, "tf": timeframe}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
