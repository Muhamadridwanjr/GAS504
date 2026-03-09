from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from src.api.dependencies import verify_internal_api_key, get_trade_service, get_analysis_service
from src.api.models import (
    InternalTradeCreate, InternalAnalysisCreate,
    TradeResponse, TradeUpdate, AnalysisResponse,
)
from src.core.trade_service import TradeService
from src.core.analysis_service import AnalysisService
from src.core.exceptions import TradeNotFoundError

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.post("/trades", response_model=TradeResponse, status_code=201)
async def create_trade(
    body: InternalTradeCreate,
    _: bool = Depends(verify_internal_api_key),
    service: TradeService = Depends(get_trade_service),
):
    """Mencatat trade baru (dari gas-terminal-service atau orchestrator)."""
    trade = await service.create_trade(body.model_dump())
    return TradeResponse.model_validate(trade)


@router.patch("/trades/{trade_id}", response_model=TradeResponse)
async def update_trade(
    trade_id: UUID,
    body: TradeUpdate,
    _: bool = Depends(verify_internal_api_key),
    service: TradeService = Depends(get_trade_service),
):
    """Update trade (misal saat close position)."""
    try:
        update_data = body.model_dump(exclude_unset=True)
        trade = await service.update_trade(trade_id, update_data)
        return TradeResponse.model_validate(trade)
    except TradeNotFoundError:
        raise HTTPException(status_code=404, detail="Trade not found")


@router.post("/analysis", response_model=AnalysisResponse, status_code=201)
async def create_analysis(
    body: InternalAnalysisCreate,
    _: bool = Depends(verify_internal_api_key),
    service: AnalysisService = Depends(get_analysis_service),
):
    """Mencatat analisis baru (dari gas-engine-orchestrator)."""
    analysis = await service.create_analysis(body.model_dump())
    return AnalysisResponse.model_validate(analysis)
