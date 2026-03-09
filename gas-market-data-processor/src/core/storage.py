import json
from src.lib.logger import get_logger
from src.models.ohlc import OhlcModel

logger = get_logger(__name__)

async def save_candle(redis_client, symbol: str, timeframe: str, candle: OhlcModel, max_candles: int = 1000):
    """Saves a fully formed candle to Redis for a specific timeframe."""
    key = f"ohlc:{symbol}:{timeframe}"
    last_key = f"ohlc:{symbol}:{timeframe}:last"
    
    # Save the whole history
    await redis_client.lpush(key, candle.model_dump_json())
    await redis_client.ltrim(key, 0, max_candles - 1)
    
    # Update the metadata/latest candle for quick access
    await redis_client.set(last_key, candle.model_dump_json())
    
async def update_ongoing_candle(redis_client, symbol: str, timeframe: str, candle: dict):
    """Updates the currently forming candle for quick access by other services."""
    key = f"ohlc:{symbol}:{timeframe}:ongoing"
    await redis_client.set(key, json.dumps(candle))

async def get_ohlc(redis_client, symbol: str, timeframe: str, count: int = 100, from_time: int = None, to_time: int = None):
    """Retrieves OHLC data from Redis."""
    key = f"ohlc:{symbol}:{timeframe}"
    raw_data = await redis_client.lrange(key, 0, count - 1)
    
    # Since we LPUSH, the latest is at index 0. Reversing is usually needed for chart drawing (oldest first).
    candles = [OhlcModel.model_validate_json(item) for item in reversed(raw_data)]
    
    if from_time and to_time:
        candles = [c for c in candles if from_time <= c.time <= to_time]
    
    return candles

async def get_last_candle(redis_client, symbol: str, timeframe: str):
    """Retrieves the last fully completed candle."""
    key = f"ohlc:{symbol}:{timeframe}:last"
    data = await redis_client.get(key)
    if data:
        return OhlcModel.model_validate_json(data)
    return None

async def get_all_symbols(redis_client):
    """Finds all symbols available by scanning keys."""
    keys = await redis_client.keys("ohlc:*:last")
    symbols = set()
    for key in keys:
        parts = key.decode("utf-8").split(":")
        if len(parts) >= 2:
            symbols.add(parts[1])
    return list(symbols)
