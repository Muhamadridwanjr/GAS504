from src.lib.utils import parse_timeframe_to_seconds, get_candle_start_time
from src.lib.logger import get_logger
from src.models.ohlc import OhlcModel
from src.core.storage import save_candle, update_ongoing_candle

logger = get_logger(__name__)

# In-memory store for forming candles per symbol & timeframe
# Format: {(symbol, timeframe): {"time": ..., "open": ..., ...}}
_ONGOING_CANDLES = {}

async def _resample_tick_to_timeframe(
    redis_client,
    symbol: str, 
    price: float, 
    volume: float, 
    timestamp: int, 
    timeframe: str, 
    max_candles: int
):
    """Process a single tick to update a specific timeframe."""
    tf_seconds = parse_timeframe_to_seconds(timeframe)
    candle_time = get_candle_start_time(timestamp, tf_seconds)
    
    key = (symbol, timeframe)
    
    if key not in _ONGOING_CANDLES:
        _ONGOING_CANDLES[key] = {
            "time": candle_time,
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": volume
        }
    else:
        ongoing = _ONGOING_CANDLES[key]
        
        # Determine if we've moved to a new candle
        if candle_time > ongoing["time"]:
            # Close out the old candle
            completed_candle = OhlcModel(**ongoing)
            await save_candle(redis_client, symbol, timeframe, completed_candle, max_candles)
            
            # Start a new candle
            _ONGOING_CANDLES[key] = {
                "time": candle_time,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": volume
            }
        else:
            # Update ongoing candle
            ongoing["high"] = max(ongoing["high"], price)
            ongoing["low"] = min(ongoing["low"], price)
            ongoing["close"] = price
            ongoing["volume"] += volume
            
    # Send the ongoing update to Redis so frontend/other engines can see LIVE candle action
    await update_ongoing_candle(redis_client, symbol, timeframe, _ONGOING_CANDLES[key])

async def process_tick_for_all_timeframes(
    redis_client, 
    symbol: str, 
    price: float, 
    volume: float, 
    timestamp: int, 
    timeframes: list[str], 
    max_candles: int
):
    """Resamples a tick into all requested timeframes simultaneously."""
    for tf in timeframes:
        await _resample_tick_to_timeframe(redis_client, symbol, price, volume, timestamp, tf, max_candles)
