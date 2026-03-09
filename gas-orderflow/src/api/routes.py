from fastapi import APIRouter, HTTPException
from src.api.models import TickInput, OrderFlowMetrics, LiquidityResponse, LiquidityZone
from src.core.accumulator import accumulator
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/orderflow/tick")
async def ingest_tick(tick: TickInput):
    """Ingest a single tick into the accumulator."""
    accumulator.ingest_tick(
        symbol=tick.symbol,
        price=tick.last,
        volume=tick.volume,
        side=tick.side
    )
    return {"status": "ok", "symbol": tick.symbol}

@router.get("/orderflow/{symbol}/current", response_model=OrderFlowMetrics)
async def get_current_metrics(symbol: str):
    metrics = accumulator.get_metrics(symbol)
    return OrderFlowMetrics(**metrics)

@router.get("/orderflow/{symbol}/liquidity", response_model=LiquidityResponse)
async def get_liquidity_zones(symbol: str):
    zones_raw = accumulator.get_liquidity_zones(symbol)
    zones = [LiquidityZone(**z) for z in zones_raw]
    return LiquidityResponse(symbol=symbol, zones=zones)

@router.get("/orderflow/{symbol}/signal")
async def get_signal(symbol: str):
    metrics = accumulator.get_metrics(symbol)
    return {
        "symbol": symbol,
        "pressure": metrics["pressure"],
        "delta": metrics["delta"],
        "imbalance": metrics["imbalance"],
        "strength": min(abs(metrics["imbalance"]) * 2, 1.0)
    }

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "gas-orderflow"}
