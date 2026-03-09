import numpy as np
import talib
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("ADX")
def get_adx(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.ADX(data["high"], data["low"], data["close"], timeperiod=period)}

@register_indicator("DI")
def get_di(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    plus_di = talib.PLUS_DI(data["high"], data["low"], data["close"], timeperiod=period)
    minus_di = talib.MINUS_DI(data["high"], data["low"], data["close"], timeperiod=period)
    plus_dm = talib.PLUS_DM(data["high"], data["low"], timeperiod=period)
    minus_dm = talib.MINUS_DM(data["high"], data["low"], timeperiod=period)
    return {"plus_di": plus_di, "minus_di": minus_di, "plus_dm": plus_dm, "minus_dm": minus_dm}

@register_indicator("AROON")
def get_aroon(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    aroon_down, aroon_up = talib.AROON(data["high"], data["low"], timeperiod=period)
    aroon_osc = talib.AROONOSC(data["high"], data["low"], timeperiod=period)
    return {"up": aroon_up, "down": aroon_down, "oscillator": aroon_osc}

@register_indicator("SAR")
def get_sar(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    acceleration = kwargs.get("acceleration", 0.02)
    maximum = kwargs.get("maximum", 0.2)
    return {"default": talib.SAR(data["high"], data["low"], acceleration=acceleration, maximum=maximum)}
