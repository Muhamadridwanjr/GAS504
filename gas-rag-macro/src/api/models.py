"""
Pydantic models for gas-rag-macro API.
"""
from __future__ import annotations
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────────────────────────

class MacroAnalyzeRequest(BaseModel):
    """Request body for POST /macro/analyze."""

    symbol: str = Field(..., examples=["XAUUSD"], description="Trading symbol to analyze")
    query: str = Field(..., description="Natural language question about the macro outlook")
    time_horizon: Literal["1h", "24h", "1w", "1m"] = Field("24h", description="Analysis time horizon")
    include_news: bool = Field(True, description="Include latest news articles")
    include_calendar: bool = Field(True, description="Include economic calendar events")
    include_price_data: bool = Field(True, description="Include current price data")
    model_preference: Literal["vertex", "openai"] = Field("openai", description="Preferred AI provider")
    temperature: float = Field(0.3, ge=0.0, le=1.0)
    max_tokens: int = Field(1200, ge=100, le=4096)


# ── Response sub-models ───────────────────────────────────────────────────────

class KeyFactor(BaseModel):
    factor: str
    impact: str
    probability: float = Field(..., ge=0.0, le=1.0)


class NewsArticle(BaseModel):
    title: str
    source: str
    time: str
    url: Optional[str] = None
    sentiment: Optional[str] = None


class CalendarEvent(BaseModel):
    event: str
    date: str
    forecast: Optional[str] = None
    previous: Optional[str] = None
    impact: Literal["low", "medium", "high"] = "medium"


# ── Main Response ─────────────────────────────────────────────────────────────

class MacroAnalyzeResponse(BaseModel):
    """Response from POST /macro/analyze."""

    id: str
    symbol: str
    timestamp: int
    summary: str
    sentiment: Literal["bullish", "bearish", "neutral"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    key_factors: list[KeyFactor] = []
    news: list[NewsArticle] = []
    calendar_events: list[CalendarEvent] = []
    historical_reaction: Optional[str] = None
    sources: list[str] = []
    provider_used: str
    model_used: str
    processing_time_ms: int


# ── Health / Info ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


class ProviderInfo(BaseModel):
    name: str
    available: bool
    model: str


class ProvidersResponse(BaseModel):
    providers: list[ProviderInfo]
    default: str


class KnowledgeUpdateResponse(BaseModel):
    status: str
    message: str
    documents_indexed: Optional[int] = None
