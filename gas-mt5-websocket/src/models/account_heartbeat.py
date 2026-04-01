from pydantic import BaseModel
from typing import List, Optional

class PositionData(BaseModel):
    ticket: Optional[int] = 0
    symbol: str
    direction: str        # "BUY" or "SELL"
    lot: Optional[float] = 0.0          # Optional for old EAs
    entry_price: Optional[float] = 0.0   # Optional for old EAs
    current_price: Optional[float] = 0.0
    pnl: Optional[float] = 0.0           # Optional for old EAs
    profit: Optional[float] = 0.0        # Support old EAs field name
    swap: Optional[float] = 0.0
    magic: Optional[int] = 0
    comment: Optional[str] = ""
    open_time: Optional[str] = ""

class AccountHeartbeatData(BaseModel):
    """Per-user EA account heartbeat — does NOT need to send tick/OHLC data."""
    user_id: str
    account_id: Optional[int] = 0
    broker: Optional[str] = ""
    server: Optional[str] = ""
    currency: Optional[str] = "USD"
    leverage: Optional[int] = 100
    balance: float
    equity: float
    margin: Optional[float] = 0.0
    free_margin: Optional[float] = 0.0
    margin_level: Optional[float] = 0.0
    floating_pnl: Optional[float] = 0.0
    daily_pnl: Optional[float] = 0.0
    positions_count: Optional[int] = 0
    positions: Optional[List[PositionData]] = []
    ea_version: Optional[str] = "1.0"
    symbol: Optional[str] = "XAUUSD"
