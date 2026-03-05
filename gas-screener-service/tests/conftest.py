import pytest

SAMPLE_INDICATORS = {
    "RSI": {"value": 35.5, "signal": "oversold"},
    "EMA_20": {"value": 1910.5},
    "EMA_50": {"value": 1920.0},
    "MACD": {"value": -5.2, "signal": -3.1, "histogram": -2.1},
}

SAMPLE_SMC = {
    "trend": "bearish",
    "structure": "BOS",
    "order_block": {"detected": True, "direction": "bearish"},
    "fvg": {"detected": False},
}
