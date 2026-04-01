from pydantic import BaseModel
from typing import List, Optional

class TickData(BaseModel):
    time: float           # Some EAs send as float
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    volume: Optional[int] = 0

class TickBatch(BaseModel):
    symbol: str
    ticks: List[TickData]
