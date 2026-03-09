from pydantic import BaseModel

class RiskEvaluateRequest(BaseModel):
    account_id: str
    symbol: str
    signal: str
    entry_price: float
    confidence: float
    account_balance: float
    current_drawdown: float

class RiskEvaluateResponse(BaseModel):
    approved: bool
    lot_size: float
    adjusted_sl: float
    adjusted_tp: float
    reason: str
    risk_amount: float
