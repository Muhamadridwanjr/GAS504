from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class AlertCreate(BaseModel):
    """Schema to create a new alert."""
    name: Optional[str] = Field(None, max_length=255, description="Nama alert (opsional)")
    symbol: str = Field(..., max_length=20, description="Aset (XAUUSD, BTCUSD, dll)")
    timeframe: Optional[str] = Field(None, max_length=10, description="M1, M5, H1, dll (null = semua)")
    condition: dict = Field(..., description="Struktur kondisi JSON")
    cooldown: int = Field(0, ge=0, description="Cooldown dalam detik (0 = tidak ada)")
    active: bool = Field(True, description="Apakah alert aktif")
    metadata_info: Optional[dict[str, Any]] = None


class AlertUpdate(BaseModel):
    """Schema to update an existing alert."""
    name: Optional[str] = None
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    condition: Optional[dict] = None
    cooldown: Optional[int] = None
    active: Optional[bool] = None
    metadata_info: Optional[dict[str, Any]] = None


class AlertResponse(BaseModel):
    """Schema for alert response."""
    id: UUID
    user_id: UUID
    name: Optional[str] = None
    symbol: str
    timeframe: Optional[str] = None
    condition: dict
    cooldown: int
    last_triggered: Optional[datetime] = None
    active: bool
    metadata_info: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Paginated list of alerts."""
    total: int
    limit: int
    offset: int
    data: list[AlertResponse]


class AlertHistoryResponse(BaseModel):
    """Schema for alert trigger history."""
    id: UUID
    alert_id: UUID
    triggered_at: datetime
    trigger_data: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class AlertHistoryListResponse(BaseModel):
    total: int
    data: list[AlertHistoryResponse]


class EvaluateRequest(BaseModel):
    """Schema for manual evaluation request."""
    alert_id: UUID
    market_data: dict = Field(..., description="Data pasar untuk evaluasi")


class EvaluateResponse(BaseModel):
    """Schema for manual evaluation response."""
    alert_id: UUID
    triggered: bool
    condition: dict
    market_data: dict
