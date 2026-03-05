"""
Pydantic models for screener API requests and responses.
"""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


class ScreenerCondition(BaseModel):
    type: str = Field(..., description="'indicator' or 'smc'")
    name: str = Field(..., description="e.g. RSI, FVG, OrderBlock")
    period: int | None = None
    operator: str | None = None
    value: float | None = None
    direction: str | None = None
    lookback: int | None = None


class ScreenerRequest(BaseModel):
    symbols: list[str] = Field(default_factory=list)
    timeframe: str = "H1"
    conditions: list[ScreenerCondition] = Field(default_factory=list)
    logic: str = Field(default="AND", description="AND or OR")
    include_metadata: bool = True


class ScreenerResult(BaseModel):
    symbol: str
    indicators: dict[str, Any] = Field(default_factory=dict)
    smc: dict[str, Any] = Field(default_factory=dict)


class ScreenerResponse(BaseModel):
    total: int
    results: list[ScreenerResult]
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
