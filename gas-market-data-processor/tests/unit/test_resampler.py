import pytest
from src.core.resampler import process_tick_for_all_timeframes, _ONGOING_CANDLES

@pytest.mark.asyncio
async def test_resampler_multiple_timeframes(mock_redis):
    _ONGOING_CANDLES.clear()
    symbol = "XAUUSD"
    timeframes = ["M1", "M5"]
    max_candles = 100
    
    # Tick 1
    await process_tick_for_all_timeframes(mock_redis, symbol, 1500.0, 1.0, 1700000000, timeframes, max_candles)
    assert (symbol, "M1") in _ONGOING_CANDLES
    assert _ONGOING_CANDLES[(symbol, "M1")]["close"] == 1500.0
    
    # Tick 2, inside the same M1 candle
    await process_tick_for_all_timeframes(mock_redis, symbol, 1505.0, 2.0, 1700000030, timeframes, max_candles)
    assert _ONGOING_CANDLES[(symbol, "M1")]["high"] == 1505.0
    assert _ONGOING_CANDLES[(symbol, "M1")]["volume"] == 3.0
    
    # Tick 3, outside the M1 candle (60s later), crosses boundary
    await process_tick_for_all_timeframes(mock_redis, symbol, 1495.0, 1.0, 1700000065, timeframes, max_candles)
    
    # It should have called save_candle for M1
    assert mock_redis.lpush.called
    assert mock_redis.ltrim.called
    
    # Ensure current candle is reset properly
    assert _ONGOING_CANDLES[(symbol, "M1")]["open"] == 1495.0
    assert _ONGOING_CANDLES[(symbol, "M1")]["volume"] == 1.0
