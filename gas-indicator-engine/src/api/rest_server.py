from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from src.lib.logger import log

app = FastAPI(title="GAS Indicator Engine REST API", version="1.0.0")

class IndicatorRequest(BaseModel):
    name: str
    periods: List[int]
    params: Optional[Dict[str, Any]] = None

class CalculateRequest(BaseModel):
    symbol: str
    timeframe: str
    ohlc: Optional[List[Dict[str, Any]]] = None
    indicators: List[IndicatorRequest]
    options: Optional[Dict[str, str]] = None

@app.get("/health")
def health_check():
    """Health check endpoint used by Docker and API Gateway."""
    return {"status": "ok", "service": "gas-indicator-engine"}

from src.api.dependencies import get_api_key
from fastapi import Depends

from src.indicators import calculate_all as calc_ind
from src.data.redis_provider import RedisProvider
from src.lib.config import settings

redis_provider = RedisProvider(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_PASSWORD)

@app.post("/calculate")
def calculate_indicators(req: CalculateRequest, api_key: str = Depends(get_api_key)):
    """
    Kalkulasi indikator teknikal untuk symbol dan timeframe yang diberikan.
    """
    log.info(f"Received calculate request for {req.symbol} on timeframe {req.timeframe}")
    
    # Get Data
    ohlc_data = req.ohlc
    if not ohlc_data:
        ohlc_data = redis_provider.get_ohlc(req.symbol, req.timeframe)
        
    results = calc_ind(ohlc_data, req.indicators)
    
    return {
        "results": results
    }
