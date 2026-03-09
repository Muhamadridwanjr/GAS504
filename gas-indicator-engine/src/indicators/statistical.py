import numpy as np
import talib
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("BETA")
def get_beta(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 5)
    return {"default": talib.BETA(data["high"], data["low"], timeperiod=period)}

@register_indicator("CORREL")
def get_correl(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 30)
    return {"default": talib.CORREL(data["high"], data["low"], timeperiod=period)}

@register_indicator("LINEARREG")
def get_linearreg(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    value = talib.LINEARREG(data["close"], timeperiod=period)
    angle = talib.LINEARREG_ANGLE(data["close"], timeperiod=period)
    slope = talib.LINEARREG_SLOPE(data["close"], timeperiod=period)
    return {"value": value, "angle": angle, "slope": slope}

@register_indicator("STDDEV")
def get_stddev(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 5)
    nbdev = kwargs.get("nbdev", 1.0)
    return {"default": talib.STDDEV(data["close"], timeperiod=period, nbdev=nbdev)}
