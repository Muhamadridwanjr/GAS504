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
