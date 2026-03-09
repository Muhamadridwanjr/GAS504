from pydantic import BaseModel
from typing import Optional
from enum import Enum

class OrderAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"

class TradeRequest(BaseModel):
    symbol: str
    action: OrderAction
    order_type: OrderType
    volume: float
    price: float = 0.0 # 0 for market
    stop_loss: float = 0.0
    take_profit: float = 0.0
    comment: Optional[str] = ""

class StatusUpdate(BaseModel):
    order_id: str
    status: str
    fill_price: float = 0.0
    fill_time: Optional[int] = 0
    commission: float = 0.0
    swap: float = 0.0
    profit: float = 0.0
