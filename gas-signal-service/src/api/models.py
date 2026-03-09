from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime

class SignalCreate(BaseModel):
    tier: str = Field(..., description="insider, premium, ultimate")
    source: str = Field(default="user_id or orchestrator")
    symbol: str
    timeframe: Optional[str] = None
    action: str = Field(..., description="BUY or SELL")
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: Optional[float] = None
    metadata_info: Optional[dict[str, Any]] = None

class SignalResponse(BaseModel):
    id: UUID
    tier: str
    source: str
    symbol: str
    timeframe: Optional[str] = None
    action: str
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: Optional[float] = None
    metadata_info: Optional[dict[str, Any]] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True

class SignalListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[SignalResponse]
