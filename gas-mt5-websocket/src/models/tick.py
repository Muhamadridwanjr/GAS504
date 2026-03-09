from pydantic import BaseModel
from typing import List, Optional

class TickData(BaseModel):
    time: int
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    volume: Optional[int] = 0

class TickBatch(BaseModel):
    symbol: str
    ticks: List[TickData]
