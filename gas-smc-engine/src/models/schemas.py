from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum


class TradingStyle(str, Enum):
    SCALPING = "scalping"
    INTRADAY = "intraday"
    SWING    = "swing"


class DetectionOptions(BaseModel):
    trading_style:   TradingStyle = TradingStyle.INTRADAY
    include_filters: List[str]    = ["kill_zones", "amd"]
    detect:          List[str]    = ["market_structure", "zones", "liquidity", "entry"]


class OHLCVCandle(BaseModel):
    time:   int
    open:   float
    high:   float
    low:    float
    close:  float
    volume: float = 0.0


class DetectRequest(BaseModel):
    symbol:    str
    timeframe: str = "H1"
    # candles: list of OHLCV dicts — primary input
    candles:   List[OHLCVCandle]
    options:   DetectionOptions = Field(default_factory=DetectionOptions)


class DetectResponse(BaseModel):
    symbol:           str
    timeframe:        str
    trading_style:    str
    market_structure: Dict[str, Any]
    zones:            Dict[str, Any]
    liquidity:        Dict[str, Any]
    entry:            Dict[str, Any]
    time_context:     Dict[str, Any]
    signal:           Dict[str, Any]
    confluence_score: int
    candle_count:     int
