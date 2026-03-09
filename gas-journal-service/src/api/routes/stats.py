from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional
from datetime import datetime
from src.api.dependencies import get_user_id, get_stats_service
from src.api.models import StatsResponse
from src.core.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("", response_model=StatsResponse)
async def get_stats(
    user_id: UUID = Depends(get_user_id),
    service: StatsService = Depends(get_stats_service),
    symbol: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
):
    """Statistik performa trading user (win rate, profit factor, drawdown, dll)."""
    stats = await service.get_stats(
        user_id=user_id,
        symbol=symbol,
        from_date=from_date,
        to_date=to_date,
    )
    return StatsResponse(**stats)
