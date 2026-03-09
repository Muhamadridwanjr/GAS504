from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from uuid import UUID
from src.api.models import SignalCreate, SignalResponse, SignalListResponse
from src.api.dependencies import get_signal_service, get_current_user
from src.core.service import SignalCoreService
from src.lib.logger import logger

router = APIRouter(prefix="/signals", tags=["Signals"])

@router.post("", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def create_signal(
    signal_data: SignalCreate,
    service: SignalCoreService = Depends(get_signal_service),
    user: dict = Depends(get_current_user)
):
    """
    Create a new trading signal. Needs auth.
    """
    try:
        data = signal_data.model_dump()
        # Override source with user ID if not provided explicitly by an admin/system
        if user.get("role") != "admin" and user.get("role") != "service":
            data['source'] = user['user_id']
            
        signal = await service.create_new_signal(data)
        logger.info(f"Signal {signal.id} created by {data['source']}")
        return signal
    except Exception as e:
        logger.error(f"Error creating signal: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("", response_model=SignalListResponse)
async def get_signals(
    tier: Optional[str] = Query(None, description="Comma separated tiers"),
    symbol: Optional[str] = Query(None),
    timeframe: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    service: SignalCoreService = Depends(get_signal_service),
    user: dict = Depends(get_current_user)
):
    """
    Get signals based on user allowed tier (validated via billing).
    """
    filters = {
        "tier": tier,
        "symbol": symbol,
        "limit": limit,
        "offset": offset
    }
    
    signals, total = await service.get_signals_for_user(user["user_id"], user["token"], filters)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": signals
    }

@router.get("/{id}", response_model=SignalResponse)
async def get_signal_by_id(
    id: UUID,
    service: SignalCoreService = Depends(get_signal_service),
    user: dict = Depends(get_current_user)
):
    # Retrieve and check auth. Simplified for this layer.
    signal = await service.repo.get_signal_by_id(id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_signal(
    id: UUID,
    service: SignalCoreService = Depends(get_signal_service),
    user: dict = Depends(get_current_user)
):
    if user.get("role") not in ["admin", "service"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete signals")
        
    success = await service.delete_signal(id)
    if not success:
        raise HTTPException(status_code=404, detail="Signal not found")

@router.post("/{id}/expire", response_model=dict)
async def set_signal_expired(
    id: UUID,
    service: SignalCoreService = Depends(get_signal_service),
    user: dict = Depends(get_current_user)
):
    success = await service.expire(id)
    if not success:
        raise HTTPException(status_code=404, detail="Signal not found")
    return {"message": "Signal expired successfully"}
