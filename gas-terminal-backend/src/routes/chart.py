import httpx
from fastapi import APIRouter, HTTPException, Query
from src.config import settings
from src.services.client import get_client

router = APIRouter(tags=["Chart"])

@router.get("/terminal/chart/{symbol}")
async def get_chart_data(
    symbol: str,
    timeframe: str = Query("15m"),
    from_time: str = Query(None),
    to_time: str = Query(None)
):
    """
    Proxy to gas-chart-service /api/v1/chart/{symbol}
    """
    client = await get_client()
    try:
        params = {"timeframe": timeframe}
        if from_time: params["from_time"] = from_time
        if to_time: params["to_time"] = to_time
        
        url = f"{settings.CHART_SERVICE_URL}/api/v1/chart/{symbol}"
        resp = await client.get(url, params=params)
        
        if resp.status_code == 200:
            return resp.json()
            
        return {"status": "error", "message": f"Upstream error {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/terminal/chart/{symbol}/history")
async def get_chart_history(
    symbol: str,
    timeframe: str = Query("M15"),
    from_time: int = Query(None),
    to_time: int = Query(None),
    count: int = Query(None),
    include_volume: bool = Query(True)
):
    """
    Proxy to gas-mt5-data-service /history
    Get real OHLCV data from MT5
    """
    client = await get_client()
    try:
        params = {"symbol": symbol, "timeframe": timeframe, "include_volume": include_volume}
        if from_time: params["from_time"] = from_time
        if to_time: params["to_time"] = to_time
        if count: params["count"] = count
        
        url = f"{settings.MT5_DATA_URL}/history"
        resp = await client.get(url, params=params)
        
        if resp.status_code == 200:
            return resp.json()
            
        return {"status": "error", "message": f"Upstream MT5 error {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
