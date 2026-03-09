from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class BaseMessage(BaseModel):
    type: str

class RegisterMessage(BaseMessage):
    type: Literal["register"] = "register"
    symbols: List[str]

class TickMessage(BaseMessage):
    type: Literal["tick"] = "tick"
    symbol: str
    time: int
    bid: float
    ask: float
    volume: float = 0.0

class OhlcMessage(BaseMessage):
    type: Literal["ohlc"] = "ohlc"
    symbol: str
    timeframe: str
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

class PingMessage(BaseMessage):
    type: Literal["ping"] = "ping"

class PongMessage(BaseMessage):
    type: Literal["pong"] = "pong"

class ErrorMessage(BaseMessage):
    type: Literal["error"] = "error"
    message: str
