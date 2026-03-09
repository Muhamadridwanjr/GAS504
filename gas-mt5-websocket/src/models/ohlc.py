from pydantic import BaseModel
from typing import Optional

class OHLCData(BaseModel):
    symbol: str
    timeframe: str
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: int
