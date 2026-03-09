import pytest
import numpy as np
from src.indicators.moving_averages import calculate_sma, calculate_indicators
from src.models.protobuf import indicator_pb2

def test_calculate_sma():
    prices = np.array([10.0, 11.0, 12.0, 13.0, 14.0], dtype=np.float64)
    result = calculate_sma(prices, 3)
    
    assert len(result) == 5
    assert np.isnan(result[0])
    assert np.isnan(result[1])
    assert result[2] == 11.0  # (10+11+12)/3
    assert result[3] == 12.0  # (11+12+13)/3
    assert result[4] == 13.0  # (12+13+14)/3

def test_calculate_indicators():
    data = [
        {"time": 1, "open": 10, "high": 12, "low": 9, "close": 10, "volume": 100},
        {"time": 2, "open": 10, "high": 12, "low": 9, "close": 11, "volume": 100},
        {"time": 3, "open": 10, "high": 12, "low": 9, "close": 12, "volume": 100},
        {"time": 4, "open": 10, "high": 12, "low": 9, "close": 13, "volume": 100},
        {"time": 5, "open": 10, "high": 12, "low": 9, "close": 14, "volume": 100},
    ]
    
    class MockReq:
        def __init__(self, name, periods):
            self.name = name
            self.periods = periods

    req = [MockReq("SMA", [3])]
    results = calculate_indicators(data, req)
    
    assert len(results) == 1
    assert results[0]["name"] == "SMA"
    assert results[0]["period"] == 3
    assert results[0]["values"] == [0.0, 0.0, 11.0, 12.0, 13.0]
    assert results[0]["timestamps"] == [1, 2, 3, 4, 5]
