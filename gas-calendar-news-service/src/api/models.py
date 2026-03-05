from pydantic import BaseModel, Field
from typing import Any, Optional

class EventResponse(BaseModel):
    total: int = 0
    data: list[dict] = Field(default_factory=list)

class SummaryResponse(BaseModel):
    summary: str
    event_count: int = 0

class HealthResponse(BaseModel):
    status: str; service: str; version: str; environment: str
