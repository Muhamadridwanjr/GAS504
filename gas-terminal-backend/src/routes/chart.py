import httpx
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Response
from src.config import settings
from src.services.client import get_client

router = APIRouter(tags=["Chart"])

class ChartDataRequest(BaseModel):
    timeframe: str
    from_ts: Optional[int] = None
    to_ts: Optional[int] = None
    count: Optional[int] = None
    indicators: Optional[List[Dict[str, Any]]] = None
    include_smc: bool = False

@router.post("/terminal/chart/{symbol}/data")
async def get_chart_combined_data(symbol: str, req: ChartDataRequest):
    """
    Proxy to gas-chart-service /chart/data
    Get combined OHLCV, Indicators, and SMC data
    """
    client = await get_client()
    try:
        url = f"{settings.CHART_SERVICE_URL}/chart/data"
        payload = req.model_dump()
        payload["symbol"] = symbol
        
        headers = {"X-Internal-Key": settings.GATEWAY_API_KEY or "gas-internal-super-secret-key"}
        resp = await client.post(url, json=payload, headers=headers)
        
        if resp.status_code == 200:
            return resp.json()
            
        return {"status": "error", "message": f"Upstream Chart Service error {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
        
        url = f"{settings.CHART_SERVICE_URL}/chart/{symbol}"
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

@router.get("/terminal/chart/{symbol}/render")
async def render_chart_proxy(symbol: str, timeframe: str = "M15", count: int = 100):
    """
    Proxy to gas-chart-service /chart/render/{symbol}
    Returns a PNG image of the chart
    """
    client = await get_client()
    try:
        url = f"{settings.CHART_SERVICE_URL}/chart/render/{symbol}"
        params = {"timeframe": timeframe, "count": count}
        headers = {"X-Internal-Key": settings.GATEWAY_API_KEY or "gas-internal-super-secret-key"}
        
        resp = await client.get(url, params=params, headers=headers)
        
        if resp.status_code == 200:
            return Response(content=resp.content, media_type="image/png")
            
        raise HTTPException(resp.status_code, detail=f"Upstream Error: {resp.text}")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(500, detail=str(e))
