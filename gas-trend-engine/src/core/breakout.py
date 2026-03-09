from src.lib.logger import get_logger

logger = get_logger(__name__)

def evaluate_breakout(features: dict, period: int = 20) -> dict:
    """
    Breakout trend signal: BUY if close > highest(high, N), SELL if close < lowest(low, N).
    """
    close = features.get("close", 0)
    highest = features.get(f"highest_{period}", features.get("highest_20", 0))
    lowest = features.get(f"lowest_{period}", features.get("lowest_20", 0))
    adx = features.get("adx", 0)

    signal = "NEUTRAL"
    strength = 0.0

    if close >= highest and highest > 0:
        signal = "BUY"
        strength = min(0.6 + (adx / 100), 0.99)
    elif close <= lowest and lowest > 0:
        signal = "SELL"
        strength = min(0.6 + (adx / 100), 0.99)

    return {
        "signal": signal,
        "strength": round(strength, 2),
        "method": "breakout",
        "details": {
            f"highest_{period}": highest,
            f"lowest_{period}": lowest,
            "adx": adx
        }
    }
