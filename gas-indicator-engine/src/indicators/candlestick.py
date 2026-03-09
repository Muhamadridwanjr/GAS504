import numpy as np
import talib
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("CDLDOJI")
def get_doji(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLDOJI(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLHAMMER")
def get_hammer(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLHAMMER(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLINVERTEDHAMMER")
def get_inverted_hammer(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLINVERTEDHAMMER(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLHANGINGMAN")
def get_hanging_man(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLHANGINGMAN(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLSHOOTINGSTAR")
def get_shooting_star(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLSHOOTINGSTAR(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLENGULFING")
def get_engulfing(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLENGULFING(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLMORNINGSTAR")
def get_morning_star(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLMORNINGSTAR(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLEVENINGSTAR")
def get_evening_star(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLEVENINGSTAR(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDL3WHITESOLDIERS")
def get_3_white_soldiers(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDL3WHITESOLDIERS(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDL3BLACKCROWS")
def get_3_black_crows(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDL3BLACKCROWS(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLHARAMI")
def get_harami(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLHARAMI(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLDARKCLOUDCOVER")
def get_dark_cloud_cover(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLDARKCLOUDCOVER(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLPIERCING")
def get_piercing(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLPIERCING(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("CDLMARUBOZU")
def get_marubozu(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.CDLMARUBOZU(data["open"], data["high"], data["low"], data["close"])}
