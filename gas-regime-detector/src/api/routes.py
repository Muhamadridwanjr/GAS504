from fastapi import APIRouter
from typing import List
from src.api.models import RegimeRequest, BatchRegimeRequest, RegimeResponse
from src.core.classifier import classifier
from src.cache.redis_cache import cache
from src.config import settings

router = APIRouter()

@router.post("/regime", response_model=RegimeResponse)
async def get_regime(req: RegimeRequest):
    # 1. Check cache
    cache_key = f"regime:{req.symbol}:{req.timeframe}"
    cached_data = await cache.get(cache_key)
    
    if cached_data:
        return RegimeResponse(**cached_data)

    # 2. Process features using selected classifier
    detector = classifier.get_detector()
    regime_name, confidence, details = detector.detect(req.features)
    
    details["regime_method"] = settings.regime_method

    response_data = {
        "symbol": req.symbol,
        "timeframe": req.timeframe,
        "regime": regime_name,
        "confidence": confidence,
        "details": details
    }
    
    # 3. Cache and return
    await cache.set(cache_key, response_data)
    
    return RegimeResponse(**response_data)

@router.post("/regime/batch", response_model=List[RegimeResponse])
async def get_regime_batch(req: BatchRegimeRequest):
    results = []
    for r in req.requests:
        res = await get_regime(r)
        results.append(res)
    return results
