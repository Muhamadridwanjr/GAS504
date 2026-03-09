import numpy as np
import talib
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("HT_TRENDMODE")
def get_ht_trendmode(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.HT_TRENDMODE(data["close"])}

@register_indicator("HT_SINE")
def get_ht_sine(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    sine, leadsine = talib.HT_SINE(data["close"])
    return {"sine": sine, "leadsine": leadsine}

@register_indicator("HT_TRENDLINE")
def get_ht_trendline(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.HT_TRENDLINE(data["close"])}

@register_indicator("MAMA")
def get_mama(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    fastlimit = kwargs.get("fastlimit", 0.5)
    slowlimit = kwargs.get("slowlimit", 0.05)
    mama, fama = talib.MAMA(data["close"], fastlimit=fastlimit, slowlimit=slowlimit)
    return {"mama": mama, "fama": fama}
