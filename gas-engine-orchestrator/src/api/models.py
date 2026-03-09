from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AnalyzeRequest(BaseModel):
    symbol: str = Field(..., description="Pasangan mata uang/aset (contoh: XAUUSD)")
    timeframe: str = Field(..., description="Timeframe (contoh: H1, M15)")
    indicators: List[str] = Field(default=[], description="Daftar indikator (contoh: ['RSI', 'MA'])")
    smc: bool = Field(default=True, description="Flag untuk mendeteksi SMC")

class AnalyzeResponse(BaseModel):
    symbol: str
    timeframe: str
    timestamp: int
    indicators: Dict[str, Any]
    smc: Dict[str, Any]
    signal: str

class SignalRequest(BaseModel):
    symbol: str
    timeframe: str
    strategy: str

class StrategyDetail(BaseModel):
    name: str
    version: str

class SignalResponse(BaseModel):
    symbol: str
    signal: str
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
