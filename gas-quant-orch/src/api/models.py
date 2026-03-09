from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AnalyzeRequest(BaseModel):
    symbol: str
    timeframe: str = "H1"
    features: Optional[Dict[str, Any]] = None
    engines: Optional[List[str]] = ["regime", "pattern", "statarb"]

class AnalyzeResponse(BaseModel):
    symbol: str
    timeframe: str
    signal: str
    confidence: float
    score: float
    details: Dict[str, Any]

class BatchAnalyzeRequest(BaseModel):
    requests: List[AnalyzeRequest]


# ── GAS AI Signal Request/Response (for EA integration) ──────────────
class GASSignalRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M15"
    market: Optional[Dict[str, Any]] = None   # bid, ask, spread, atr_14_m15
    session: str = "OFF"                       # LONDON, NEW_YORK, OFF
    context: Optional[Dict[str, Any]] = None  # balance, daily_pnl, consecutive_loss, etc.
    engines: Optional[List[str]] = ["regime", "pattern", "statarb"]

class GASSignalResponse(BaseModel):
    signal_id: str
    action: str              # BUY | SELL | NONE | WAIT
    symbol: str
    entry: float
    sl: float
    tp1: float
    tp_final: float
    lot: float
    reason: str
    observation: str
    trading_plan: str
    risk_management: str
    journal: str
    backtest: str
    psychology: str
    mindset: str
    regime: str
    session: str
    confidence: float
