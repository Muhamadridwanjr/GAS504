from pydantic import BaseModel
from typing import Dict, Any, Optional

class PhaseRequest(BaseModel):
    symbol: str
    timeframe: str = "H1"

class PhaseDetails(BaseModel):
    price_vs_ema50: str
    adx: float
    volume_ratio: float
    breakout_detected: bool

class PhaseResponse(BaseModel):
    symbol: str
    timeframe: str
    phase: str
    confidence: float
    details: PhaseDetails
