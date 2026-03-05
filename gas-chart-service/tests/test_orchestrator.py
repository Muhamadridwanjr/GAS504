"""Unit tests for ChartOrchestrator — all clients are mocked."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


SAMPLE_OHLC = [
    {"timestamp": 1700000000, "open": 1900, "high": 1910, "low": 1895, "close": 1905},
    {"timestamp": 1700003600, "open": 1905, "high": 1915, "low": 1900, "close": 1910},
]
SAMPLE_INDICATORS = {"RSI": {"value": 42.0}}
SAMPLE_SMC = {"trend": "bullish"}


@pytest.mark.asyncio
async def test_get_chart_data_basic():
    """ChartOrchestrator returns OHLC + indicators + smc merged."""
    with patch("src.core.orchestrator.MT5DataClient") as MockMT5,          patch("src.core.orchestrator.IndicatorClient") as MockInd,          patch("src.core.orchestrator.SMCClient") as MockSMC:

        MockMT5.return_value.get_ohlc = AsyncMock(return_value=SAMPLE_OHLC)
        MockInd.return_value.calculate = AsyncMock(return_value=SAMPLE_INDICATORS)
        MockSMC.return_value.detect = AsyncMock(return_value=SAMPLE_SMC)

        from src.core.orchestrator import ChartOrchestrator
        cache = AsyncMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()

        orch = ChartOrchestrator(cache)
        result = await orch.get_chart_data(
            "XAUUSD", "H1", count=2,
            indicators=[{"name": "RSI", "period": 14}],
            include_smc=True,
        )

        assert result["symbol"] == "XAUUSD"
        assert result["timeframe"] == "H1"
        assert len(result["data"]) == 2
        assert result["indicators"] == SAMPLE_INDICATORS
        assert result["smc"] == SAMPLE_SMC


@pytest.mark.asyncio
async def test_get_chart_data_cache_hit():
    """When cache returns data, no upstream clients are called."""
    cached = {"symbol": "XAUUSD", "timeframe": "H1", "data": SAMPLE_OHLC, "indicators": {}, "smc": {}}

    with patch("src.core.orchestrator.MT5DataClient") as MockMT5,          patch("src.core.orchestrator.IndicatorClient") as MockInd:

        from src.core.orchestrator import ChartOrchestrator
        cache = AsyncMock()
        cache.get = AsyncMock(return_value=cached)

        orch = ChartOrchestrator(cache)
        result = await orch.get_chart_data("XAUUSD", "H1")

        assert result == cached
        MockMT5.return_value.get_ohlc.assert_not_called()


@pytest.mark.asyncio
async def test_get_chart_data_no_indicators():
    """When no indicators requested, indicator client is not called."""
    with patch("src.core.orchestrator.MT5DataClient") as MockMT5,          patch("src.core.orchestrator.IndicatorClient") as MockInd,          patch("src.core.orchestrator.SMCClient") as MockSMC:

        MockMT5.return_value.get_ohlc = AsyncMock(return_value=SAMPLE_OHLC)

        from src.core.orchestrator import ChartOrchestrator
        cache = AsyncMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()

        orch = ChartOrchestrator(cache)
        result = await orch.get_chart_data("XAUUSD", "H1", include_smc=False)

        MockInd.return_value.calculate.assert_not_called()
        assert result["data"] == SAMPLE_OHLC
