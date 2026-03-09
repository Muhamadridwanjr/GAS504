from pydantic import BaseModel
from typing import Optional, Dict

class SignalRequest(BaseModel):
    pair: str
    lookback: Optional[int] = None
    threshold: Optional[float] = None

class SignalResponse(BaseModel):
    pair: str
    signal: str
    zscore: float
    hedge_ratio: float
    spread: float
    entry_prices: Dict[str, float]
    confidence: float

class PairConfig(BaseModel):
    pair: str
    symbol_x: str
    symbol_y: str
