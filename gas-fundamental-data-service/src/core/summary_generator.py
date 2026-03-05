"""Generate text summaries from fundamental data."""
from __future__ import annotations

def generate_fundamental_summary(symbol: str, indicator: str, data: list[dict], period: str = "month") -> str:
    if not data:
        return f"No {indicator} data available for {symbol}."
    latest = data[0]
    oldest = data[-1] if len(data) > 1 else data[0]
    change = latest["value"] - oldest["value"]
    direction = "increased" if change > 0 else "decreased" if change < 0 else "remained stable"
    return (f"{symbol} {indicator}: Latest value is {latest['value']}"
            f"{' ' + latest.get('unit','') if latest.get('unit') else ''}. "
            f"Over the period, {indicator} {direction} by {abs(change):.4f}. "
            f"Data points: {len(data)}.")
