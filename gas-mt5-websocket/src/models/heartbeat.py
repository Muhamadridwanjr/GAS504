from pydantic import BaseModel

class HeartbeatData(BaseModel):
    symbol: str
    balance: float
    equity: float
    positions: int
    magic: int
