from enum import Enum
from pydantic import BaseModel

class OhlcModel(BaseModel):
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class TickModel(BaseModel):
    time: int
    price: float
    volume: float
