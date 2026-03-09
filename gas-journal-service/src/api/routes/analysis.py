from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional
from src.api.dependencies import get_user_id, get_analysis_service
from src.api.models import AnalysisResponse, AnalysisListResponse
from src.core.analysis_service import AnalysisService
from src.core.exceptions import AnalysisNotFoundError
from fastapi import HTTPException

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("", response_model=AnalysisListResponse)
async def list_analysis(
    user_id: UUID = Depends(get_user_id),
    service: AnalysisService = Depends(get_analysis_service),
    symbol: Optional[str] = Query(None),
    timeframe: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Mendapatkan daftar analisis milik user."""
    analyses, total = await service.list_analyses(user_id, {
        "symbol": symbol,
        "timeframe": timeframe,
        "limit": limit,
        "offset": offset,
    })
    return AnalysisListResponse(
        total=total,
        limit=limit,
        offset=offset,
        data=[AnalysisResponse.model_validate(a) for a in analyses],
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    user_id: UUID = Depends(get_user_id),
    service: AnalysisService = Depends(get_analysis_service),
):
    """Detail satu analisis."""
    try:
        analysis = await service.get_analysis(analysis_id, user_id)
        return AnalysisResponse.model_validate(analysis)
    except AnalysisNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: UUID,
    user_id: UUID = Depends(get_user_id),
    service: AnalysisService = Depends(get_analysis_service),
):
    """Soft delete analisis milik user."""
    try:
        await service.delete_analysis(analysis_id, user_id)
        return {"message": "Analysis deleted successfully"}
    except AnalysisNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
