from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from src.api.models import FeatureRequest, BatchFeatureRequest, FeatureResponse
from src.core.calculator import compute_features
from src.core.market_data_client import MarketDataClient
from src.cache.redis_cache import cache
import pandas as pd

router = APIRouter()
market_client = MarketDataClient()

@router.post("/features", response_model=FeatureResponse)
async def get_features(req: FeatureRequest):
    # 1. Check cache (sort features to ensure consistent cache key)
    feat_str = ",".join(sorted(req.features))
    cache_key = f"features:{req.symbol}:{req.timeframe}:{req.limit}:{feat_str}"
    
    cached_data = await cache.get(cache_key)
    if cached_data:
        return FeatureResponse(symbol=req.symbol, timeframe=req.timeframe, data=cached_data)

    # 2. Fetch market data
    # To compute features correctly, we need more data points than requested by the limit
    # e.g., for SMA-50, we need at least 50 points. Let's fetch limit + 100 for safety.
    fetch_limit = min(1000, req.limit + 100)
    
    df = await market_client.get_ohlc(req.symbol, req.timeframe, limit=fetch_limit)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No market data available for {req.symbol}")

    # 3. Calculate features
    result_df = compute_features(df, req.features)
    
    # Clean up results
    # Replace NaN/inf with None for JSON serialization
    result_df = result_df.replace([pd.NA, float('inf'), float('-inf')], None)
    
    # We only want the last `limit` rows where features are mostly calculated
    # Drop rows that have NaN in ANY requested feature column (usually the beginning rows)
    result_df = result_df.dropna(subset=req.features, how='all')
    
    if result_df.empty:
        raise HTTPException(status_code=400, detail="Could not compute features with available data limit")
        
    result_df = result_df.tail(req.limit)

    # Convert to list of dicts
    # In Pandas > 2.0, replace pd.NA with None manually
    records = []
    for record in result_df.to_dict(orient="records"):
        cleaned_record = {k: (None if pd.isna(v) else v) for k, v in record.items()}
        records.append(cleaned_record)
        
    # 4. Cache and return
    await cache.set(cache_key, records)

    return FeatureResponse(
        symbol=req.symbol,
        timeframe=req.timeframe,
        data=records
    )

@router.post("/features/batch")
async def get_features_batch(req: BatchFeatureRequest) -> Dict[str, Any]:
    # Simplified batch processing
    results = {}
    for sym in req.symbols:
        try:
            # Reusing original single logic
            single_req = FeatureRequest(
                symbol=sym,
                timeframe=req.timeframe,
                features=req.features,
                limit=req.limit
            )
            res = await get_features(single_req)
            results[sym] = res.data
        except Exception as e:
            results[sym] = {"error": str(e)}
            
    return results
