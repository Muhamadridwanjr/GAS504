from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class RegimeRequest(BaseModel):
    symbol: str
    timeframe: str
    features: Dict[str, float]

class BatchRegimeRequest(BaseModel):
    requests: List[RegimeRequest]

class RegimeResponse(BaseModel):
    symbol: str
    timeframe: str
    regime: str
    confidence: float
    details: Dict[str, Any]
