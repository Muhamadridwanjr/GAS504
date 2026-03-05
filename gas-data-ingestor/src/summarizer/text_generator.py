"""
Generate text summaries from OHLCV data per period.
"""
from __future__ import annotations

import pandas as pd

from src.lib.logger import get_logger

logger = get_logger(__name__)


def generate_summary(df: pd.DataFrame, symbol: str, period: str = "month") -> list[dict]:
    """
    Generate text summaries from a DataFrame grouped by period.

    Args:
        df: DataFrame with columns timestamp, open, high, low, close, volume (optional).
        symbol: Trading symbol (e.g. XAUUSD).
        period: Grouping period — 'day', 'week', 'month', or 'year'.

    Returns:
        List of dicts with keys: period_label, text, metadata.
    """
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    freq_map = {"day": "D", "week": "W", "month": "ME", "year": "YE"}
    freq = freq_map.get(period, "ME")

    summaries: list[dict] = []
    grouped = df.set_index("timestamp").resample(freq)

    for label, group in grouped:
        if group.empty:
            continue

        o = group["open"].iloc[0]
        c = group["close"].iloc[-1]
        h = group["high"].max()
        l = group["low"].min()  # noqa: E741
        vol = int(group["volume"].sum()) if "volume" in group.columns else 0
        ret = ((c - o) / o * 100) if o else 0
        volatility = ((h - l) / l * 100) if l else 0

        period_label = str(label.date()) if hasattr(label, "date") else str(label)

        text = (
            f"{symbol} {period} ending {period_label}: "
            f"Open {o:.2f}, Close {c:.2f}, High {h:.2f}, Low {l:.2f}. "
            f"Volume {vol:,}. Return {ret:+.2f}%, Volatility {volatility:.2f}%."
        )

        summaries.append({
            "period_label": period_label,
            "text": text,
            "metadata": {
                "symbol": symbol,
                "period": period,
                "open": float(o),
                "close": float(c),
                "high": float(h),
                "low": float(l),
                "volume": vol,
                "return_pct": round(ret, 4),
                "volatility_pct": round(volatility, 4),
            },
        })

    logger.info("Generated %d summaries for %s (%s)", len(summaries), symbol, period)
    return summaries
