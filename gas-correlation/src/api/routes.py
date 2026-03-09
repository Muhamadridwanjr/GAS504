from fastapi import APIRouter, HTTPException, Query
from src.api.models import BiasRequest, BiasResponse, CorrelationMatrixResponse, PairCorrelationResponse
from src.core.calculator import CorrelationCalculator
from src.core.bias import BiasCalculator
from src.core.asset_manager import AssetManager
from src.cache.redis_cache import cache
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
calculator = CorrelationCalculator()
bias_calc = BiasCalculator()
asset_mgr = AssetManager()

@router.get("/correlation/matrix", response_model=CorrelationMatrixResponse)
async def get_correlation_matrix(window: int = Query(20)):
    cache_key = f"corr:matrix:{window}"
    cached = await cache.get(cache_key)
    if cached:
        return CorrelationMatrixResponse(**cached)

    returns = await asset_mgr.get_return_series(count=max(window, 100))
    matrix = calculator.compute_correlation_matrix(returns, window=window)
    result = CorrelationMatrixResponse(window=window, matrix=matrix)
    await cache.set(cache_key, result.model_dump())
    return result

@router.get("/correlation/pair", response_model=PairCorrelationResponse)
async def get_pair_correlation(
    symbol1: str = Query(...),
    symbol2: str = Query(...),
    window: int = Query(20)
):
    returns = await asset_mgr.get_return_series(count=max(window, 100))
    corr = calculator.get_pair_correlation(returns, symbol1, symbol2, window=window)
    return PairCorrelationResponse(symbol1=symbol1, symbol2=symbol2, window=window, correlation=corr)

@router.post("/bias", response_model=BiasResponse)
async def get_bias(request: BiasRequest):
    returns = await asset_mgr.get_return_series(count=max(request.window, 100))
    matrix = calculator.compute_correlation_matrix(returns, window=request.window)
    if request.symbol not in matrix:
        raise HTTPException(status_code=404, detail=f"Symbol {request.symbol} not found in monitored assets")
    latest_returns = await asset_mgr.get_latest_returns()
    bias_result = bias_calc.calculate_bias(request.symbol, matrix[request.symbol], latest_returns, threshold=request.threshold)
    return BiasResponse(**bias_result)

@router.get("/assets")
async def get_assets():
    return {"assets": asset_mgr.assets}

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "gas-correlation"}
