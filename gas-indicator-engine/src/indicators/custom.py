import numpy as np
import pandas as pd
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("PRICE_CHANGE")
def get_price_change(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    close = data["close"]
    # Change from previous close
    res = np.zeros_like(close)
    res[1:] = np.diff(close)
    res[0] = np.nan
    return {"default": res}

@register_indicator("HIGH_LOW_RATIO")
def get_high_low_ratio(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    # Avoid division by zero
    low = np.where(data["low"] == 0, 1e-9, data["low"])
    return {"default": data["high"] / low}

@register_indicator("CLOSE_OPEN_RATIO")
def get_close_open_ratio(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    # Avoid division by zero
    open_price = np.where(data["open"] == 0, 1e-9, data["open"])
    return {"default": data["close"] / open_price}

@register_indicator("VOLATILITY_30D")
def get_volatility_30d(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 30)
    close = pd.Series(data["close"])
    returns = close.pct_change()
    volatility = returns.rolling(window=period).std()
    return {"default": volatility.values}

@register_indicator("PRICE_VOLATILITY_30D")
def get_price_volatility_30d(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 30)
    close = pd.Series(data["close"])
    volatility = close.rolling(window=period).std()
    return {"default": volatility.values}
