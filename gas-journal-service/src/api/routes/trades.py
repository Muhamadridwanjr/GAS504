from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional
from datetime import datetime
from src.api.dependencies import get_user_id, get_trade_service
from src.api.models import TradeResponse, TradeListResponse
from src.core.trade_service import TradeService
from src.core.exceptions import TradeNotFoundError
from fastapi import HTTPException

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.get("", response_model=TradeListResponse)
async def list_trades(
    user_id: UUID = Depends(get_user_id),
    service: TradeService = Depends(get_trade_service),
    symbol: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: str = Query("-entry_time"),
):
    """Mendapatkan daftar trade milik user (via gateway)."""
    trades, total = await service.list_trades(user_id, {
        "symbol": symbol,
        "status": status,
        "from_date": from_date,
        "to_date": to_date,
        "limit": limit,
        "offset": offset,
        "sort": sort,
    })
    return TradeListResponse(
        total=total,
        limit=limit,
        offset=offset,
        data=[TradeResponse.model_validate(t) for t in trades],
    )


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: UUID,
    user_id: UUID = Depends(get_user_id),
    service: TradeService = Depends(get_trade_service),
):
    """Detail satu trade."""
    try:
        trade = await service.get_trade(trade_id, user_id)
        return TradeResponse.model_validate(trade)
    except TradeNotFoundError:
        raise HTTPException(status_code=404, detail="Trade not found")


@router.delete("/{trade_id}")
async def delete_trade(
    trade_id: UUID,
    user_id: UUID = Depends(get_user_id),
    service: TradeService = Depends(get_trade_service),
):
    """Soft delete trade milik user."""
    try:
        await service.delete_trade(trade_id, user_id)
        return {"message": "Trade deleted successfully"}
    except TradeNotFoundError:
        raise HTTPException(status_code=404, detail="Trade not found")
