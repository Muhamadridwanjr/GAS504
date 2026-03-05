from pydantic import BaseModel, Field
from typing import Any
class ChartDataRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "H1"
    from_ts: int | None = Field(None, alias="from")
    to_ts: int | None = Field(None, alias="to")
    count: int | None = 100
    indicators: list[dict] | None = None
    include_smc: bool = False
class TemplateCreateRequest(BaseModel):
    name: str
    layout: dict = Field(default_factory=dict)
class HealthResponse(BaseModel):
    status: str; service: str; version: str; environment: str
