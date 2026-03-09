from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DetectRequest(BaseModel):
    symbol: str
    timeframe: str
    features: List[float]
    top_k: Optional[int] = None # Will default to settings
    min_confidence: Optional[float] = None

class BatchDetectRequest(BaseModel):
    requests: List[DetectRequest]

class DetectResponse(BaseModel):
    symbol: str
    timeframe: str
    confidence: float
    expected_return: float
    direction: str
    probability_up: float
    details: Dict[str, Any]
