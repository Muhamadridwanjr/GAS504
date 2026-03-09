from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum

class TradingStyle(str, Enum):
    SCALPING = "scalping"
    INTRADAY = "intraday"
    SWING = "swing"

class Timeframes(BaseModel):
    tf1: str
    tf2: str
    tf3: str
    tf4: str

class DetectionOptions(BaseModel):
    trading_style: TradingStyle = TradingStyle.INTRADAY
    include_filters: List[str] = ["kill_zones", "amd"]
    detect: List[str] = ["market_structure", "zones", "liquidity", "entry"]

class DetectRequest(BaseModel):
    symbol: str
    timeframes: Timeframes
    ohlc: Dict[str, Any]
    options: DetectionOptions = Field(default_factory=DetectionOptions)

class DetectResponse(BaseModel):
    symbol: str
    trading_style: str
    timeframes: Dict[str, str]
    market_structure: Dict[str, Any]
    zones: Dict[str, Any]
    liquidity: Dict[str, Any]
    entry: Dict[str, Any]
    signal: Dict[str, Any]
