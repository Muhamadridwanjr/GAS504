from fastapi import APIRouter
from typing import Dict, Any
from src.api.models import AnalyzeRequest, AnalyzeResponse, BatchAnalyzeRequest, GASSignalRequest, GASSignalResponse
from src.core.orchestrator import orchestrator
from src.cache.redis_cache import cache
import json

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_symbol(req: AnalyzeRequest):
    # Try Cache
    cache_key = f"orch:analyze:{req.symbol}:{req.timeframe}"
    cached = await cache.get(cache_key)
    if cached:
        return AnalyzeResponse(**cached)
        
    result = await orchestrator.analyze(req.symbol, req.timeframe, req.engines)
    
    # Store in Cache
    await cache.set(cache_key, result)
    return AnalyzeResponse(**result)

@router.post("/analyze/batch", response_model=Dict[str, Any])
async def analyze_batch(req: BatchAnalyzeRequest):
    results = {}
    for r in req.requests:
        try:
            res = await orchestrator.analyze(r.symbol, r.timeframe, r.engines)
            results[f"{r.symbol}_{r.timeframe}"] = res
        except Exception as e:
             results[f"{r.symbol}_{r.timeframe}"] = {"error": str(e)}
    return results

@router.get("/engines")
async def active_engines():
    return {
        "regime": "active",
        "pattern": "active",
        "statarb": "active"
    }


@router.post("/signal/generate")
async def generate_gas_signal(req: GASSignalRequest):
    """
    Generate full GAS AI signal for GASSTRATEGYEAPRO v4.0 EA.
    Receives EA context (market data, account info) and returns
    a complete signal with entry/sl/tp/reason/psychology/mindset.
    """
    # Check cache first (5s TTL to avoid duplicate signals on rapid polls)
    cache_key = f"orch:gas_signal:{req.symbol}:{req.session}"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    result = await orchestrator.generate_gas_signal(
        symbol=req.symbol,
        timeframe=req.timeframe,
        market=req.market,
        session=req.session,
        context=req.context,
        engines=req.engines,
    )

    # Cache for 5 seconds to prevent duplicate signals
    if result.get("action") not in ("NONE", "WAIT", ""):
        await cache.set(cache_key, result, ttl=5)

    return result
