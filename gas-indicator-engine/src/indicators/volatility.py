import numpy as np
import talib
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("BBANDS")
def get_bbands(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 20)
    nbdevup = kwargs.get("nbdevup", 2.0)
    nbdevdn = kwargs.get("nbdevdn", 2.0)
    upper, middle, lower = talib.BBANDS(
        data["close"], timeperiod=period, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0
    )
    return {"upper": upper, "middle": middle, "lower": lower}

@register_indicator("ATR")
def get_atr(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.ATR(data["high"], data["low"], data["close"], timeperiod=period)}

@register_indicator("NATR")
def get_natr(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.NATR(data["high"], data["low"], data["close"], timeperiod=period)}

@register_indicator("TRANGE")
def get_trange(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.TRANGE(data["high"], data["low"], data["close"])}

@register_indicator("TYPPRICE")
def get_typprice(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.TYPPRICE(data["high"], data["low"], data["close"])}
