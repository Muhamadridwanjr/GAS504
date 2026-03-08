"""Pydantic models for fundamental data API."""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field

class FundamentalDataPoint(BaseModel):
    time: int
    value: float
    unit: str = ""

class FundamentalResponse(BaseModel):
    symbol: str
    indicator: str
    data: list[FundamentalDataPoint] = Field(default_factory=list)

class FundamentalSummaryResponse(BaseModel):
    symbol: str
    indicator: str
    summary: str
    period: str = "month"

class FundamentalCreateRequest(BaseModel):
    symbol: str
    indicator: str
    time: int
    value: float
    unit: str = ""
    source: str = ""

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


# ── Macro Dashboard ────────────────────────────────────────────────────────

class MacroHistoryPoint(BaseModel):
    date: str
    value: float

class MacroIndicator(BaseModel):
    key: str
    label: str
    region: str
    assets: list[str]
    tier: int
    impact: str
    unit: str
    period: str
    actual: Optional[float] = None
    previous: Optional[float] = None
    forecast: Optional[float] = None
    release_date: Optional[str] = None
    surprise: Optional[float] = None
    surprise_direction: Optional[str] = None
    status: str = "released"
    history: list[MacroHistoryPoint] = Field(default_factory=list)
    ai_notes: str = ""
    scraped_at: Optional[str] = None

class MacroDashboardResponse(BaseModel):
    last_updated: str
    indicators: list[MacroIndicator]
