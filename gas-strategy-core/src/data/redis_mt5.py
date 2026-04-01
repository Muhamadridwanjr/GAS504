import redis.asyncio as aioredis
import json
import os
from typing import Optional
from src.data.binance_fetcher import is_crypto_pair, get_ohlc_from_binance, get_latest_price_binance

REDIS_URL     = os.getenv("REDIS_URL",     "redis://localhost:6379/0")
REDIS_HOT_URL = os.getenv("REDIS_HOT_URL", REDIS_URL)  # ephemeral tick data

_redis     = None   # cold Redis — credits, sessions, analysis cache
_redis_hot = None   # hot Redis  — MT5 OHLC tick data (no persistence)


async def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


async def get_redis_hot():
    """Hot Redis for ephemeral tick / OHLC data written by MT5 EA."""
    global _redis_hot
    if _redis_hot is None:
        _redis_hot = aioredis.from_url(REDIS_HOT_URL, decode_responses=True)
    return _redis_hot

async def get_ohlc(symbol: str, timeframe: str, limit: int = 200) -> list:
    """Get OHLC candles from hot Redis (tick data), sorted oldest-first for indicator calc."""
    r = await get_redis_hot()
    key = f"ohlc:{symbol}:{timeframe}"
    raw = await r.lrange(key, 0, limit - 1)  # newest first
    candles = []
    for item in raw:
        try:
            candles.append(json.loads(item))
        except Exception:
            pass
    # Sort ascending by time (oldest first) for indicator calculation
    candles.sort(key=lambda x: x.get("time", 0))
    return candles

async def get_latest_price(symbol: str) -> Optional[float]:
    """Get latest close price for a symbol (from hot Redis)."""
    r = await get_redis_hot()
    # Try H1 first, then M1, then H4
    for tf in ["H1", "M1", "H4"]:
        key = f"ohlc:{symbol}:{tf}"
        raw = await r.lindex(key, 0)  # Most recent
        if raw:
            try:
                data = json.loads(raw)
                return float(data.get("close", 0))
            except Exception:
                pass
    return None

async def get_account(user_id: str) -> Optional[dict]:
    """Get MT5 account data for a user (from hot Redis — EA pushes on each tick)."""
    r = await get_redis_hot()
    key = f"account:{user_id}"
    raw = await r.get(key)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    return None

async def get_positions(user_id: str) -> list:
    """Get open positions for a user (from hot Redis — EA pushes on each tick)."""
    r = await get_redis_hot()
    key = f"account:{user_id}:positions"
    raw = await r.get(key)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    return []

async def get_ohlc_smart(symbol: str, timeframe: str, limit: int = 200) -> list:
    """
    Smart OHLC fetcher:
    - Crypto pairs (BTC/USDT, ETH/USDT, etc.) → gas-binance-service
    - Forex/Commodity pairs (XAUUSD, EURUSD, etc.) → MT5 Redis
    """
    if is_crypto_pair(symbol):
        return await get_ohlc_from_binance(symbol, timeframe, limit)
    return await get_ohlc(symbol, timeframe, limit)


async def get_latest_price_smart(symbol: str) -> Optional[float]:
    """Get latest price — Binance for crypto, Redis for forex."""
    if is_crypto_pair(symbol):
        return await get_latest_price_binance(symbol)
    return await get_latest_price(symbol)


async def get_all_symbols_with_data() -> list:
    """Get all symbols that have OHLC data in hot Redis."""
    r = await get_redis_hot()
    keys = await r.keys("ohlc:*:H1")
    symbols = []
    for key in keys:
        parts = key.split(":")
        if len(parts) >= 2:
            symbols.append(parts[1])
    return symbols
