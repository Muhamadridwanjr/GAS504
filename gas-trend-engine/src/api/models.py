from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class TrendRequest(BaseModel):
    symbol: str
    timeframe: str = "H1"
    method: str = "both"  # "breakout", "ma_cross", "both"
    breakout_period: int = 20
    ma_fast: int = 10
    ma_slow: int = 30
    adx_threshold: int = 25

class TrendResponse(BaseModel):
    symbol: str
    timeframe: str
    signal: str
    strength: float
    method: str
    entry_price: float
    stop_loss: float
    take_profit: float
    details: Dict[str, Any] = {}
