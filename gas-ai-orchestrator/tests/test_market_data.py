import pytest
from unittest.mock import AsyncMock, patch
from src.core.market_data import market_data

@pytest.mark.asyncio
async def test_build_multi_tf_ohlcv_success():
    # Mock data service response
    mock_candles = [
        {"time": 1709758800, "open": 2100.0, "high": 2105.0, "low": 2095.0, "close": 2102.0, "volume": 100}
    ]
    
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": mock_candles}
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get.return_value = mock_response
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        # Also mock get_latest_price to avoid Redis dependency
        with patch.object(market_data, "get_latest_price", return_value=2102.5):
            result = await market_data.build_multi_tf_ohlcv("XAUUSD")
            
            assert "HISTORICAL OHLCV" in result
            assert "XAUUSD" in result
            assert "H4" in result
            assert "H1" in result
            assert "M15" in result
            assert "M5" in result
            assert "2102.50000" in result
            assert "2100.000" in result

@pytest.mark.asyncio
async def test_build_multi_tf_ohlcv_service_failure_fallback():
    mock_response = AsyncMock()
    mock_response.status_code = 500
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get.return_value = mock_response
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        with patch.object(market_data, "get_latest_price", return_value=2102.5):
            result = await market_data.build_multi_tf_ohlcv("XAUUSD")
            
            assert "No data available" in result
            assert "[LIVE TICK PRICE]: 2102.50000" in result
