from src.core.cleaner import clean_tick, clean_ohlc
from src.core.resampler import process_tick_for_all_timeframes
from src.core.storage import save_candle
from src.lib.logger import get_logger
from src.models.ohlc import OhlcModel

logger = get_logger(__name__)

# Store last known timestamp per symbol for basic sequence validation
_LAST_TICK_TIMESTAMPS = {}

async def process_tick(
    symbol: str, 
    price: float, 
    volume: float, 
    timestamp: int, 
    redis_client, 
    timeframes: list[str], 
    max_candles: int
):
    """
    Main entrypoint for raw ticks.
    Cleanses the tick and routes to the resampler for all timeframes.
    """
    last_ts = _LAST_TICK_TIMESTAMPS.get(symbol, 0)
    
    if not clean_tick(price, volume, timestamp, last_ts):
        return  # Drop Invalid tick
        
    _LAST_TICK_TIMESTAMPS[symbol] = timestamp
    
    # Route to resampler
    await process_tick_for_all_timeframes(
        redis_client, symbol, price, volume, timestamp, timeframes, max_candles
    )

async def process_ohlc(
    symbol: str, 
    timeframe: str, 
    open: float, 
    high: float, 
    low: float, 
    close: float, 
    volume: float, 
    timestamp: int, 
    redis_client, 
    max_candles: int
):
    """
    Directly ingest pre-formed OHLC. Use this if EA sends full candles instead of ticks.
    """
    if not clean_ohlc(open, high, low, close, volume):
        logger.warning(f"Invalid OHLC data received for {symbol} at {timestamp}")
        return
        
    candle = OhlcModel(
        time=timestamp,
        open=open,
        high=high,
        low=low,
        close=close,
        volume=volume
    )
    
    await save_candle(redis_client, symbol, timeframe, candle, max_candles)
