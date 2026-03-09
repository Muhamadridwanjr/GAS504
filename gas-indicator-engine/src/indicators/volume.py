import numpy as np
import talib
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("AD")
def get_ad(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.AD(data["high"], data["low"], data["close"], data["volume"])}

@register_indicator("ADOSC")
def get_adosc(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    fastperiod = kwargs.get("fastperiod", 3)
    slowperiod = kwargs.get("slowperiod", 10)
    return {"default": talib.ADOSC(
        data["high"], data["low"], data["close"], data["volume"],
        fastperiod=fastperiod, slowperiod=slowperiod
    )}

@register_indicator("OBV")
def get_obv(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.OBV(data["close"], data["volume"])}

@register_indicator("MFI")
def get_mfi(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.MFI(data["high"], data["low"], data["close"], data["volume"], timeperiod=period)}
