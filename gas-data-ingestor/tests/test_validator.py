"""Unit tests for OHLCV validator — pure pandas, no mocking."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
import numpy as np
from src.ingestor.validator import validate_ohlcv


def make_df(**kwargs):
    """Helper: build a minimal valid OHLCV DataFrame."""
    base = {
        "timestamp": [1700000000, 1700003600, 1700007200],
        "open":  [1900.0, 1905.0, 1903.0],
        "high":  [1910.0, 1915.0, 1908.0],
        "low":   [1895.0, 1900.0, 1898.0],
        "close": [1905.0, 1910.0, 1903.0],
        "volume":[1000.0, 1200.0, 900.0],
    }
    base.update(kwargs)
    return pd.DataFrame(base)


class TestValidateOHLCV:
    def test_valid_data_passes(self):
        df = make_df()
        result = validate_ohlcv(df)
        assert len(result) == 3

    def test_drops_null_close(self):
        df = make_df(close=[1905.0, None, 1903.0])
        result = validate_ohlcv(df)
        assert len(result) == 2

    def test_drops_null_timestamp(self):
        df = make_df(timestamp=[1700000000, None, 1700007200])
        result = validate_ohlcv(df)
        assert len(result) == 2

    def test_drops_high_less_than_low(self):
        df = make_df(
            high=[1910.0, 1890.0, 1908.0],   # row 1: high < low
            low= [1895.0, 1900.0, 1898.0],
        )
        result = validate_ohlcv(df)
        assert len(result) == 2

    def test_drops_multiple_null_fields(self):
        df = make_df(
            open=[1900.0, None, 1903.0],
            high=[None,   1915.0, 1908.0],
        )
        result = validate_ohlcv(df)
        assert len(result) == 1  # only row 2 is clean

    def test_empty_dataframe_ok(self):
        df = pd.DataFrame(columns=["timestamp","open","high","low","close","volume"])
        result = validate_ohlcv(df)
        assert len(result) == 0

    def test_all_rows_invalid_returns_empty(self):
        df = make_df(close=[None, None, None])
        result = validate_ohlcv(df)
        assert len(result) == 0

    def test_returns_dataframe(self):
        df = make_df()
        result = validate_ohlcv(df)
        assert isinstance(result, pd.DataFrame)
