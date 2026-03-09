from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field


# ─── Follow ───────────────────────────────────────────────────────────────────

class FollowItem(BaseModel):
    user_id: str
    followed_at: str


class FollowListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[FollowItem]


class FollowResponse(BaseModel):
    follower_id: str
    followee_id: str
    followed_at: str


class FollowStatusResponse(BaseModel):
    is_following: bool


# ─── Insider Signal ───────────────────────────────────────────────────────────

class InsiderSignalRequest(BaseModel):
    symbol: str = Field(..., example="XAUUSD")
    timeframe: str = Field(..., example="H1")
    action: str = Field(..., example="BUY")
    entry_price: float = Field(..., example=2000.5)
    stop_loss: Optional[float] = Field(None, example=1990.0)
    take_profit: Optional[float] = Field(None, example=2020.0)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, example=0.8)
    note: Optional[str] = Field(None, example="My analysis based on ICT concepts.")


# ─── Feed ─────────────────────────────────────────────────────────────────────

class FeedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[Dict[str, Any]]


# ─── Internal ─────────────────────────────────────────────────────────────────

class SignalPostedPayload(BaseModel):
    signal_id: str
    user_id: str
    created_at: Optional[str] = None
