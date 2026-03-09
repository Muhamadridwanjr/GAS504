from pydantic import BaseModel
from typing import List, Optional

class TickInput(BaseModel):
    symbol: str
    time: int
    bid: float
    ask: float
    last: float
    volume: float
    side: str = "buy"  # "buy" or "sell"

class OrderFlowMetrics(BaseModel):
    symbol: str
    timestamp: int
    delta: float
    cumulative_delta: float
    buy_volume: float
    sell_volume: float
    imbalance: float
    pressure: str
    tick_count: int

class LiquidityZone(BaseModel):
    price: float
    volume: float
    type: str  # "support" or "resistance"

class LiquidityResponse(BaseModel):
    symbol: str
    zones: List[LiquidityZone]
