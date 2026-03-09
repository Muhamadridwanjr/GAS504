from fastapi import APIRouter, HTTPException
from typing import List
from src.api.models import TrendRequest, TrendResponse
from src.core.trend_detector import TrendDetector
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
detector = TrendDetector()

@router.post("/trend", response_model=TrendResponse)
async def get_trend(request: TrendRequest):
    try:
        result = await detector.detect(
            symbol=request.symbol,
            timeframe=request.timeframe,
            method=request.method,
            breakout_period=request.breakout_period,
            ma_fast=request.ma_fast,
            ma_slow=request.ma_slow,
            adx_threshold=request.adx_threshold
        )
        return TrendResponse(**result)
    except Exception as e:
        logger.error(f"Error detecting trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trend/batch", response_model=List[TrendResponse])
async def get_trend_batch(requests: List[TrendRequest]):
    results = []
    for req in requests:
        try:
            result = await detector.detect(
                symbol=req.symbol,
                timeframe=req.timeframe,
                method=req.method,
                breakout_period=req.breakout_period,
                ma_fast=req.ma_fast,
                ma_slow=req.ma_slow,
                adx_threshold=req.adx_threshold
            )
            results.append(TrendResponse(**result))
        except Exception:
            pass
    return results

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "gas-trend-engine"}
