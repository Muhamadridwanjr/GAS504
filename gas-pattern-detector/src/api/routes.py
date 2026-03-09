from fastapi import APIRouter
from typing import List, Dict, Any
from src.api.models import DetectRequest, BatchDetectRequest, DetectResponse
from src.core.matcher import matcher
from src.cache.redis_cache import cache
from src.config import settings

router = APIRouter()

@router.post("/detect", response_model=DetectResponse)
async def detect_pattern(req: DetectRequest):
    # Determine parameters with fallbacks to settings
    top_k = req.top_k if req.top_k is not None else settings.default_top_k
    min_confidence = req.min_confidence if req.min_confidence is not None else settings.min_confidence
    
    # 1. Check cache (using a simplified hash of features for the key)
    # Note: In production, caching float arrays exactly might be tricky due to precision.
    # Here we create a simple string representation for the cache key.
    feature_hash = hashlib.md5(str([round(f, 4) for f in req.features]).encode()).hexdigest()
    cache_key = f"pattern:{req.symbol}:{req.timeframe}:{feature_hash}:{top_k}:{min_confidence}"
    
    cached_data = await cache.get(cache_key)
    if cached_data:
        return DetectResponse(symbol=req.symbol, timeframe=req.timeframe, **cached_data)

    # 2. Detect pattern
    result = await matcher.match(req.features, top_k, min_confidence)
    
    response_data = {
        "symbol": req.symbol,
        "timeframe": req.timeframe,
        **result
    }
    
    # 3. Cache and return
    await cache.set(cache_key, result)
    
    return DetectResponse(**response_data)

@router.post("/detect/batch", response_model=Dict[str, Any])
async def detect_pattern_batch(req: BatchDetectRequest):
    results = {}
    for r in req.requests:
        try:
            res = await detect_pattern(r)
            results[r.symbol] = res.dict()
        except Exception as e:
            results[r.symbol] = {"error": str(e)}
    return results

# Helper for cache key generation
import hashlib
