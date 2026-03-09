from pydantic import BaseModel
from typing import Dict, List, Optional

class BiasRequest(BaseModel):
    symbol: str
    window: int = 20
    threshold: float = 0.7
    include_factors: bool = True

class BiasFactorItem(BaseModel):
    symbol: str
    correlation: float
    return_val: float
    contribution: str

class BiasResponse(BaseModel):
    symbol: str
    bias: str
    confidence: float
    factors: List[dict] = []

class CorrelationMatrixResponse(BaseModel):
    window: int
    matrix: Dict[str, Dict[str, float]]

class PairCorrelationResponse(BaseModel):
    symbol1: str
    symbol2: str
    window: int
    correlation: float
