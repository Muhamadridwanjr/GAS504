from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


# ─── Trade Models ────────────────────────────────────────────────

class TradeCreate(BaseModel):
    """Used by users to manually add a trade (via gateway)."""
    symbol: str
    action: str = Field(..., description="BUY or SELL")
    entry_price: float
    exit_price: Optional[float] = None
    lot: float
    profit: Optional[float] = None
    commission: Optional[float] = 0
    swap: Optional[float] = 0
    entry_time: datetime
    exit_time: Optional[datetime] = None
    status: Optional[str] = "OPEN"
    analysis_id: Optional[UUID] = None
    metadata_info: Optional[dict[str, Any]] = None


class InternalTradeCreate(BaseModel):
    """Used by internal services (terminal, orchestrator) via API key."""
    user_id: UUID
    symbol: str
    action: str = Field(..., description="BUY or SELL")
    entry_price: float
    exit_price: Optional[float] = None
    lot: float
    profit: Optional[float] = None
    commission: Optional[float] = 0
    swap: Optional[float] = 0
    entry_time: datetime
    exit_time: Optional[datetime] = None
    status: Optional[str] = "OPEN"
    analysis_id: Optional[UUID] = None
    metadata_info: Optional[dict[str, Any]] = None


class TradeUpdate(BaseModel):
    """Used to update a trade (e.g. when closing)."""
    exit_price: Optional[float] = None
    profit: Optional[float] = None
    commission: Optional[float] = None
    swap: Optional[float] = None
    exit_time: Optional[datetime] = None
    status: Optional[str] = None
    metadata_info: Optional[dict[str, Any]] = None


class TradeResponse(BaseModel):
    id: UUID
    user_id: UUID
    symbol: str
    action: str
    entry_price: float
    exit_price: Optional[float] = None
    lot: float
    profit: Optional[float] = None
    commission: Optional[float] = None
    swap: Optional[float] = None
    entry_time: datetime
    exit_time: Optional[datetime] = None
    status: str
    analysis_id: Optional[UUID] = None
    metadata_info: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TradeListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[TradeResponse]


# ─── Analysis Models ─────────────────────────────────────────────

class AnalysisCreate(BaseModel):
    """User-facing analysis create (via gateway)."""
    symbol: str
    timeframe: Optional[str] = None
    signal: str = Field(..., description="BUY, SELL, or NEUTRAL")
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    metadata_info: Optional[dict[str, Any]] = None


class InternalAnalysisCreate(BaseModel):
    """Used by internal services (orchestrator) via API key."""
    user_id: UUID
    symbol: str
    timeframe: Optional[str] = None
    signal: str = Field(..., description="BUY, SELL, or NEUTRAL")
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    metadata_info: Optional[dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    id: UUID
    user_id: UUID
    symbol: str
    timeframe: Optional[str] = None
    signal: str
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    metadata_info: Optional[dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[AnalysisResponse]


# ─── Stats Models ────────────────────────────────────────────────

class StatsResponse(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int
    win_rate: float
    total_profit: float
    total_commission: float
    total_swap: float
    net_profit: float
    average_profit: float
    average_loss: float
    average_rr: float
    max_drawdown: float
    profit_factor: float
    largest_win: float
    largest_loss: float
