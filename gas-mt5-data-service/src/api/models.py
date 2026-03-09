from pydantic import BaseModel, Field
from typing import List, Optional

class OHLCVData(BaseModel):
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: int

class HistoryResponse(BaseModel):
    symbol: str
    timeframe: str
    data: List[OHLCVData]

class ErrorResponse(BaseModel):
    detail: str
