from pydantic import BaseModel
from typing import List, Optional

class FeatureRequest(BaseModel):
    symbol: str
    timeframe: str
    features: List[str]
    from_time: Optional[int] = None
    to_time: Optional[int] = None
    limit: Optional[int] = 100

class BatchFeatureRequest(BaseModel):
    symbols: List[str]
    timeframe: str
    features: List[str]
    limit: Optional[int] = 1

class FeatureResponse(BaseModel):
    symbol: str
    timeframe: str
    data: List[dict]
