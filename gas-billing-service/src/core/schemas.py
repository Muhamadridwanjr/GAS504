from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class CreditStatus(BaseModel):
    user_id: UUID
    tier: str
    quota: int
    boost: int
    daily_usage: int
    level: int
    level_score: int

    class Config:
        from_attributes = True

class DailyCheck(BaseModel):
    can_analyze: bool
    reason: Optional[str]
    credit_type: Optional[str]
    daily_usage: int
    daily_limit: int

class AnalysisCheck(BaseModel):
    analysis_type: str

class AnalysisConsume(BaseModel):
    analysis_type: str
    status: str
