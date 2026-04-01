import json
import asyncio
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import redis.asyncio as aioredis
from ..core.binance_client import binance_client
from ..core.publisher import publisher
from ..config import settings

router = APIRouter()

# ── Redis cache for tickers ────────────────────────────────────────────────────
_redis: Optional[aioredis.Redis] = None
_TICKER_CACHE_KEY = "binance:tickers_all"
_TICKER_CACHE_TTL = 8   # seconds — refresh every 8s max

async def _get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis

def _fmt_ticker(symbol: str, t: dict) -> dict:
    return {
        "symbol": symbol,
        "last": t.get("last"),
        "bid": t.get("bid"),
        "ask": t.get("ask"),
        "volume": t.get("baseVolume"),
        "change": t.get("change"),
        "changePercent": t.get("percentage"),
        "high": t.get("high"),
        "low": t.get("low"),
    }

async def _fetch_and_cache_all() -> dict:
    """Fetch all spot tickers from Binance and store in Redis."""
    raw = await binance_client.spot.fetch_tickers()
    results = {sym: _fmt_ticker(sym, t) for sym, t in raw.items()}
    r = await _get_redis()
    await r.set(_TICKER_CACHE_KEY, json.dumps(results), ex=_TICKER_CACHE_TTL)
    return results

async def _get_cached_tickers() -> dict:
    """Return cached tickers dict, or fetch fresh if expired."""
    try:
        r = await _get_redis()
        cached = await r.get(_TICKER_CACHE_KEY)
        if cached:
            return json.loads(cached)
    except Exception:
        pass
    # Cache miss or Redis error — fetch fresh
    return await _fetch_and_cache_all()


# ── Background cache refresh task ─────────────────────────────────────────────
_cache_task: Optional[asyncio.Task] = None

async def _cache_refresher():
    """Background task: refresh ticker cache every 5 seconds."""
    while True:
        try:
            await _fetch_and_cache_all()
        except Exception:
            pass
        await asyncio.sleep(5)

def start_cache_refresher():
    global _cache_task
    if _cache_task is None or _cache_task.done():
        _cache_task = asyncio.create_task(_cache_refresher())


@router.get("/health")
async def health_check():
    start_cache_refresher()   # ensure refresher is running
    return {"status": "ok"}

@router.get("/markets")
async def get_markets():
    try:
        markets = binance_client.get_supported_markets()
        return markets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ohlcv")
async def get_ohlcv(symbol: str, timeframe: str, since: Optional[int] = None, limit: Optional[int] = Query(None, le=1000)):
    try:
        data = await binance_client.fetch_ohlcv(symbol, timeframe, since, limit)
        formatted = [
            {"time": d[0], "open": d[1], "high": d[2], "low": d[3], "close": d[4], "volume": d[5]}
            for d in data
        ]
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": formatted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ticker/{symbol:path}")
async def get_ticker(symbol: str):
    try:
        # Try cache first for spot symbols
        if ":" not in symbol:
            all_tickers = await _get_cached_tickers()
            if symbol in all_tickers:
                return all_tickers[symbol]
        data = await binance_client.fetch_ticker(symbol)
        return _fmt_ticker(symbol, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickers")
async def get_tickers(symbols: str = Query(..., description="Comma-separated symbols")):
    """Fetch multiple tickers — uses Redis cache to avoid CCXT rate-limiter contention."""
    start_cache_refresher()
    symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
    if not symbol_list:
        return {}

    # Separate spot vs futures symbols
    spot_syms    = [s for s in symbol_list if ":" not in s]
    futures_syms = [s for s in symbol_list if ":" in s]

    results = {}

    # ── Spot: serve from Redis cache ───────────────────────────────────────────
    if spot_syms:
        try:
            all_tickers = await _get_cached_tickers()
            for sym in spot_syms:
                if sym in all_tickers:
                    results[sym] = all_tickers[sym]
        except Exception:
            # Cache failure — try direct fetch for just these symbols
            try:
                raw = await asyncio.wait_for(
                    binance_client.spot.fetch_tickers(spot_syms),
                    timeout=12.0
                )
                for sym, t in raw.items():
                    if sym in spot_syms:
                        results[sym] = _fmt_ticker(sym, t)
            except Exception:
                pass

    # ── Futures: fetch directly (no cache layer yet) ────────────────────────────
    if futures_syms:
        try:
            raw = await asyncio.wait_for(
                binance_client.usdt_futures.fetch_tickers(futures_syms),
                timeout=12.0
            )
            for sym, t in raw.items():
                if sym in futures_syms:
                    results[sym] = _fmt_ticker(sym, t)
        except Exception:
            pass

    return results

@router.get("/orderbook/{symbol:path}")
async def get_order_book(symbol: str, limit: int = 10):
    try:
        data = await binance_client.fetch_order_book(symbol, limit)
        return {
            "symbol": symbol,
            "bids": data.get("bids", []),
            "asks": data.get("asks", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
