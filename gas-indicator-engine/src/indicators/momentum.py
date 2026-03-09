import numpy as np
import talib
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("RSI")
def get_rsi(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.RSI(data["close"], timeperiod=period)}

@register_indicator("MACD")
def get_macd(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    fastperiod = kwargs.get("fastperiod", 12)
    slowperiod = kwargs.get("slowperiod", 26)
    signalperiod = kwargs.get("signalperiod", 9)
    macd, macdsignal, macdhist = talib.MACD(
        data["close"], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod
    )
    return {"macd": macd, "signal": macdsignal, "histogram": macdhist}

@register_indicator("STOCH")
def get_stoch(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    fastk_period = kwargs.get("fastk_period", 5)
    slowk_period = kwargs.get("slowk_period", 3)
    slowd_period = kwargs.get("slowd_period", 3)
    slowk, slowd = talib.STOCH(
        data["high"], data["low"], data["close"],
        fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=0, slowd_period=slowd_period, slowd_matype=0
    )
    return {"slowk": slowk, "slowd": slowd}

@register_indicator("STOCHF")
def get_stochf(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    fastk_period = kwargs.get("fastk_period", 5)
    fastd_period = kwargs.get("fastd_period", 3)
    fastk, fastd = talib.STOCHF(
        data["high"], data["low"], data["close"],
        fastk_period=fastk_period, fastd_period=fastd_period, fastd_matype=0
    )
    return {"fastk": fastk, "fastd": fastd}

@register_indicator("STOCHRSI")
def get_stochrsi(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    timeperiod = kwargs.get("timeperiod", 14)
    fastk_period = kwargs.get("fastk_period", 5)
    fastd_period = kwargs.get("fastd_period", 3)
    fastk, fastd = talib.STOCHRSI(
        data["close"], timeperiod=timeperiod, fastk_period=fastk_period, fastd_period=fastd_period, fastd_matype=0
    )
    return {"fastk": fastk, "fastd": fastd}

@register_indicator("CCI")
def get_cci(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.CCI(data["high"], data["low"], data["close"], timeperiod=period)}

@register_indicator("CMO")
def get_cmo(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.CMO(data["close"], timeperiod=period)}

@register_indicator("MOM")
def get_mom(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 10)
    return {"default": talib.MOM(data["close"], timeperiod=period)}

@register_indicator("ROC")
def get_roc(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 10)
    return {"default": talib.ROC(data["close"], timeperiod=period)}

@register_indicator("WILLR")
def get_willr(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    period = kwargs.get("timeperiod", 14)
    return {"default": talib.WILLR(data["high"], data["low"], data["close"], timeperiod=period)}

@register_indicator("PPO")
def get_ppo(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    fastperiod = kwargs.get("fastperiod", 12)
    slowperiod = kwargs.get("slowperiod", 26)
    return {"default": talib.PPO(data["close"], fastperiod=fastperiod, slowperiod=slowperiod, matype=0)}

@register_indicator("APO")
def get_apo(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    fastperiod = kwargs.get("fastperiod", 12)
    slowperiod = kwargs.get("slowperiod", 26)
    return {"default": talib.APO(data["close"], fastperiod=fastperiod, slowperiod=slowperiod, matype=0)}

@register_indicator("BOP")
def get_bop(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    return {"default": talib.BOP(data["open"], data["high"], data["low"], data["close"])}

@register_indicator("ULTOSC")
def get_ultosc(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    timeperiod1 = kwargs.get("timeperiod1", 7)
    timeperiod2 = kwargs.get("timeperiod2", 14)
    timeperiod3 = kwargs.get("timeperiod3", 28)
    return {"default": talib.ULTOSC(
        data["high"], data["low"], data["close"],
        timeperiod1=timeperiod1, timeperiod2=timeperiod2, timeperiod3=timeperiod3
    )}
