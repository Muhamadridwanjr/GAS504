from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class PlanCreateRequest(BaseModel):
    title: str
    description: str = ""
    plan_date: date
    symbol: str
    direction: str  # BUY or SELL
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    notes: str = ""
    status: str = "active"

class PlanUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    plan_date: date | None = None
    symbol: str | None = None
    direction: str | None = None
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    notes: str | None = None
    status: str | None = None

class PlanResponse(BaseModel):
    id: int
    user_id: str
    title: str
    plan_date: date
    symbol: str
    direction: str
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    status: str
    created_at: str

class HealthResponse(BaseModel):
    status: str; service: str; version: str; environment: str
