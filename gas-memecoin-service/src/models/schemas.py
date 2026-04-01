from pydantic import BaseModel
from typing import Optional, List, Any

class TokenInfo(BaseModel):
    token_address: str
    symbol: str
    name: str
    chain: str
    price_usd: float
    price_change_5m: float
    price_change_1h: float
    price_change_6h: float
    price_change_24h: float
    volume_24h: float
    volume_1h: float
    liquidity_usd: float
    market_cap: Optional[float]
    fdv: Optional[float]
    buys_1h: int
    sells_1h: int
    buy_pressure: float   # buys/(buys+sells) 0..1
    age_minutes: float
    pair_address: str
    dex_url: str
    dex_id: str

class RugScore(BaseModel):
    level: str          # SAFE | RISKY | DANGER
    score: int          # 0..100 (higher = safer)
    flags: List[str]    # list of red flags detected

class AgentSignal(BaseModel):
    model: str
    signal: str         # BUY EARLY | BUY MOMENTUM | WEAK TREND | AVOID | EXIT NOW | DANGER
    score: int          # 0..100
    confidence: float
    reasoning: str

class TokenSignal(BaseModel):
    token_address: str
    symbol: str
    chain: str
    signal: str
    score: int          # composite 0..100
    risk: str           # LOW | MEDIUM | HIGH | EXTREME
    rug: RugScore
    agents: List[AgentSignal]
    consensus_signal: str
    consensus_confidence: float
    price_usd: float
    liquidity_usd: float
    volume_1h: float
    buy_pressure: float
    price_change_1h: float
    dex_url: str
    timestamp: str
