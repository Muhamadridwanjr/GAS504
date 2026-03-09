import numpy as np
import talib
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("SMA")
def get_sma(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.SMA(data["close"], timeperiod=period)}

@register_indicator("EMA")
def get_ema(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.EMA(data["close"], timeperiod=period)}

@register_indicator("WMA")
def get_wma(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.WMA(data["close"], timeperiod=period)}

@register_indicator("DEMA")
def get_dema(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.DEMA(data["close"], timeperiod=period)}

@register_indicator("TEMA")
def get_tema(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.TEMA(data["close"], timeperiod=period)}

@register_indicator("TRIMA")
def get_trima(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.TRIMA(data["close"], timeperiod=period)}

@register_indicator("KAMA")
def get_kama(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.KAMA(data["close"], timeperiod=period)}

@register_indicator("T3")
def get_t3(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.T3(data["close"], timeperiod=period)}
