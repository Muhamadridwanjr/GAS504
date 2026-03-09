import pytest
from src.core.storage import save_candle, update_ongoing_candle
from src.models.ohlc import OhlcModel

@pytest.mark.asyncio
async def test_save_candle(mock_redis):
    candle = OhlcModel(
        time=1700000000,
        open=100.0,
        high=105.0,
        low=95.0,
        close=102.0,
        volume=1000.0
    )
    await save_candle(mock_redis, "BTCUSD", "H1", candle, 10)
    
    mock_redis.lpush.assert_called_once_with("ohlc:BTCUSD:H1", candle.model_dump_json())
    mock_redis.ltrim.assert_called_once_with("ohlc:BTCUSD:H1", 0, 9)
    mock_redis.set.assert_called_once_with("ohlc:BTCUSD:H1:last", candle.model_dump_json())

@pytest.mark.asyncio
async def test_update_ongoing_candle(mock_redis):
    data = {"time": 1700000000, "close": 102.0}
    await update_ongoing_candle(mock_redis, "BTCUSD", "H1", data)
    assert mock_redis.set.called
