"""Pydantic request/response models for the API layer."""
from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field


# ─── Request Models ──────────────────────────────────────────────────────────

class SMCContext(BaseModel):
    order_blocks: list[dict[str, Any]] = []
    fvgs: list[dict[str, Any]] = []
    liquidity_levels: list[Any] = []
    structure: str | None = None


class AnalysisContext(BaseModel):
    indicators: dict[str, Any] | None = None
    smc: SMCContext | None = None


class AnalyzeRequest(BaseModel):
    symbol: str = Field(..., examples=["XAUUSD"])
    timeframe: str = Field(..., examples=["H4"])
    query: str = Field(..., examples=["Analisis struktur pasar dan level kunci"])
    context: AnalysisContext | None = None
    model_preference: Literal["vertex", "openai"] | None = None
    include_sources: bool = True
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1500, ge=100, le=4096)


class BatchAnalyzeRequest(BaseModel):
    requests: list[AnalyzeRequest]


# ─── Response Models ─────────────────────────────────────────────────────────

class KeyLevels(BaseModel):
    support: list[float] = []
    resistance: list[float] = []


class EntryInfo(BaseModel):
    price: float | None = None
    stop_loss: float | None = None
    take_profit: list[float] = []


class SourceInfo(BaseModel):
    title: str
    source: str = ""
    relevance: float = 0.0


class AnalysisResponse(BaseModel):
    id: str
    symbol: str
    timeframe: str
    timestamp: int
    summary: str
    key_levels: KeyLevels
    signal: Literal["BUY", "SELL", "NEUTRAL"]
    confidence: float
    entry: EntryInfo
    reasoning: str
    short_term_bias: str = "sideways"
    key_risks: list[str] = []
    sources: list[SourceInfo] = []
    provider_used: str
    model_used: str
    processing_time_ms: int


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


class ProviderInfo(BaseModel):
    name: str
    model: str
    available: bool


class KnowledgeStats(BaseModel):
    document_count: int
    vector_db_type: str
    status: str
