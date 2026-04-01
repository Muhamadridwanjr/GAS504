"""
GET /terminal/pairs          – Live MT5 scanner prices for all known pairs.
GET /terminal/market/{symbol}– Single-pair live snapshot from Redis.
GET /terminal/market/all     – All active scanner symbols from Redis.
"""
import json
from fastapi import APIRouter, HTTPException
from src.services.redis import redis_service

router = APIRouter()


@router.get("/terminal/pairs")
async def get_pairs():
    """Return all MT5 pairs with live prices from Redis scanner data."""
    await redis_service.connect()
    try:
        keys = await redis_service.client.keys("market:*")
        result = []
        if keys:
            pipe = redis_service.client.pipeline()
            for k in keys:
                pipe.get(k)
            values = await pipe.execute()
            for raw in values:
                if not raw:
                    continue
                try:
                    d = json.loads(raw)
                    sym = d.get("symbol", "")
                    if not sym:
                        continue
                    bid = d.get("bid", 0)
                    ask = d.get("ask", 0)
                    price = (bid + ask) / 2 if bid and ask else bid or ask
                    result.append({
                        "symbol": sym,
                        "bid": bid,
                        "ask": ask,
                        "price": price,
                        "spread": d.get("spread", 0),
                        "category": d.get("category", ""),
                        "time": d.get("time", 0),
                        "source": "mt5_live",
                    })
                except Exception:
                    continue
        return {"status": "ok", "count": len(result), "pairs": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/terminal/market/all")
async def get_all_market_data():
    """Return all active scanner symbols snapshot from Redis."""
    return await get_pairs()


@router.get("/terminal/market/{symbol}")
async def get_market_symbol(symbol: str):
    """Return live snapshot for a single symbol from MT5 scanner Redis data."""
    await redis_service.connect()
    sym = symbol.upper()
    raw = await redis_service.client.get(f"market:{sym}")
    if not raw:
        raise HTTPException(status_code=404, detail=f"No live data for {sym}.")
    try:
        d = json.loads(raw)
        bid = d.get("bid", 0)
        ask = d.get("ask", 0)
        price = (bid + ask) / 2 if bid and ask else bid or ask
        return {
            "symbol": sym,
            "bid": bid,
            "ask": ask,
            "price": price,
            "spread": d.get("spread", 0),
            "category": d.get("category", ""),
            "time": d.get("time", 0),
            "source": "mt5_live",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/terminal/market/{symbol}/ohlc")
async def get_market_ohlc(symbol: str, timeframe: str = "M15", limit: int = 200):
    """Return OHLCV candles for a symbol from MT5 scanner Redis data."""
    await redis_service.connect()
    sym = symbol.upper()
    key = f"ohlc:{sym}:{timeframe}"
    raw_list = await redis_service.client.lrange(key, 0, limit - 1)
    if not raw_list:
        raise HTTPException(status_code=404, detail=f"No OHLC data for {sym} {timeframe}.")
    candles = []
    for raw in raw_list:
        try:
            candles.append(json.loads(raw))
        except Exception:
            continue
    # lrange returns newest first — reverse for chronological order
    candles.reverse()
    return {
        "symbol": sym,
        "timeframe": timeframe,
        "count": len(candles),
        "candles": candles,
        "source": "mt5_live",
    }
