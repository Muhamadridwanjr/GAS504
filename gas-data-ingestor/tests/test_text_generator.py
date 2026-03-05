"""Unit tests for text_generator — generate_summary returns list[dict], not str."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
from src.summarizer.text_generator import generate_summary


def make_ohlcv():
    return pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
        "open":  [2800.0, 2810.0, 2820.0],
        "high":  [2820.0, 2830.0, 2840.0],
        "low":   [2790.0, 2800.0, 2810.0],
        "close": [2810.0, 2820.0, 2830.0],
        "volume":[1000.0, 1200.0, 1100.0],
    })


class TestGenerateSummary:
    def test_returns_list(self):
        df = make_ohlcv()
        result = generate_summary(df, symbol="XAUUSD", period="month")
        assert isinstance(result, list)

    def test_each_item_has_text_key(self):
        df = make_ohlcv()
        result = generate_summary(df, symbol="XAUUSD", period="month")
        assert len(result) >= 1
        assert "text" in result[0]
        assert "period_label" in result[0]
        assert "metadata" in result[0]

    def test_text_contains_symbol(self):
        df = make_ohlcv()
        result = generate_summary(df, symbol="XAUUSD", period="month")
        assert any("XAUUSD" in item["text"] for item in result)

    def test_text_contains_prices(self):
        df = make_ohlcv()
        result = generate_summary(df, symbol="XAUUSD", period="month")
        text = result[0]["text"]
        assert any(str(v) in text for v in ["2800", "2810", "2820", "2830"])

    def test_metadata_has_return_pct(self):
        df = make_ohlcv()
        result = generate_summary(df, symbol="XAUUSD", period="month")
        assert "return_pct" in result[0]["metadata"]
        assert "volatility_pct" in result[0]["metadata"]

    def test_empty_df_returns_empty_list(self):
        df = pd.DataFrame(columns=["timestamp","open","high","low","close","volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        result = generate_summary(df, symbol="XAUUSD", period="month")
        assert result == []

    def test_period_day(self):
        df = make_ohlcv()
        result = generate_summary(df, symbol="XAUUSD", period="day")
        assert len(result) == 3  # 3 days

    def test_period_month(self):
        df = make_ohlcv()
        result = generate_summary(df, symbol="XAUUSD", period="month")
        assert len(result) == 1  # all in Jan 2026
