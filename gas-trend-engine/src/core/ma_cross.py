from src.lib.logger import get_logger

logger = get_logger(__name__)

def evaluate_ma_cross(features: dict, ma_fast_period: int = 10, ma_slow_period: int = 30) -> dict:
    """
    MA Cross signal: BUY if ma_fast > ma_slow, SELL if ma_fast < ma_slow.
    """
    ma_fast = features.get(f"ema_{ma_fast_period}", features.get("ema_10", 0))
    ma_slow = features.get(f"ema_{ma_slow_period}", features.get("ema_30", 0))
    adx = features.get("adx", 0)

    signal = "NEUTRAL"
    strength = 0.0

    if ma_fast > ma_slow and ma_slow > 0:
        signal = "BUY"
        gap_pct = (ma_fast - ma_slow) / ma_slow
        strength = min(0.5 + gap_pct * 10 + (adx / 200), 0.99)
    elif ma_fast < ma_slow and ma_slow > 0:
        signal = "SELL"
        gap_pct = (ma_slow - ma_fast) / ma_slow
        strength = min(0.5 + gap_pct * 10 + (adx / 200), 0.99)

    return {
        "signal": signal,
        "strength": round(strength, 2),
        "method": "ma_cross",
        "details": {
            f"ema_{ma_fast_period}": ma_fast,
            f"ema_{ma_slow_period}": ma_slow,
            "adx": adx
        }
    }
