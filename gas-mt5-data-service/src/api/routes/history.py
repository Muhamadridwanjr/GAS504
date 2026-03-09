from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional

from src.api.models import HistoryResponse, ErrorResponse
from src.api.dependencies import get_user_id
from src.core.data_service import DataService
from src.lib.logger import logger

router = APIRouter(tags=["History"])
data_service = DataService()

@router.get("/history", response_model=HistoryResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_history(
    symbol: str = Query(..., description="Simbol, misal XAUUSD"),
    timeframe: str = Query(..., description="Timeframe: M1, M5, M15, M30, H1, H4, D1, W1, MN"),
    from_time: Optional[int] = Query(None, description="UNIX timestamp awal"),
    to_time: Optional[int] = Query(None, description="UNIX timestamp akhir"),
    count: Optional[int] = Query(None, description="Jumlah candle terakhir (jika from_time tidak ditentukan). Maks 5000."),
    include_volume: bool = Query(True, description="Sertakan volume"),
    user_id: str = Depends(get_user_id)
):
    valid_timeframes = ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN"]
    if timeframe not in valid_timeframes:
        raise HTTPException(status_code=400, detail=f"Invalid timeframe. Allowed: {valid_timeframes}")
        
    if not count and not from_time:
        count = 100 # default count
        
    if count and count > 5000:
        raise HTTPException(status_code=400, detail="Count cannot exceed 5000")

    try:
        logger.info(f"User {user_id} requesting history for {symbol} {timeframe}")
        data = await data_service.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            from_time=from_time,
            to_time=to_time,
            count=count,
            include_volume=include_volume
        )
        return HistoryResponse(
            symbol=symbol,
            timeframe=timeframe,
            data=data
        )
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
