"""
Tests for the evaluator engine.
"""

from src.core.evaluator import (
    evaluate_condition,
    evaluate_price_condition,
    evaluate_indicator_condition,
    evaluate_smc_condition,
)


class TestPriceEvaluator:
    def test_cross_above_true(self):
        condition = {"type": "price", "operator": "cross_above", "value": 2000.0}
        data = {"close": 2001.5, "prev_close": 1999.8}
        assert evaluate_price_condition(condition, data) is True

    def test_cross_above_false(self):
        condition = {"type": "price", "operator": "cross_above", "value": 2000.0}
        data = {"close": 1998.0, "prev_close": 1999.8}
        assert evaluate_price_condition(condition, data) is False

    def test_cross_below_true(self):
        condition = {"type": "price", "operator": "cross_below", "value": 2000.0}
        data = {"close": 1998.0, "prev_close": 2001.0}
        assert evaluate_price_condition(condition, data) is True

    def test_greater_than(self):
        condition = {"type": "price", "operator": "greater_than", "value": 1900.0}
        data = {"close": 2001.0}
        assert evaluate_price_condition(condition, data) is True

    def test_less_than(self):
        condition = {"type": "price", "operator": "less_than", "value": 2050.0}
        data = {"close": 2001.0}
        assert evaluate_price_condition(condition, data) is True

    def test_missing_value(self):
        condition = {"type": "price", "operator": "greater_than"}
        data = {"close": 2001.0}
        assert evaluate_price_condition(condition, data) is False


class TestIndicatorEvaluator:
    def test_rsi_less_than(self):
        condition = {"type": "indicator", "name": "RSI", "period": 14, "operator": "less_than", "value": 30}
        data = {"indicators": {"RSI_14": 28.5}}
        assert evaluate_indicator_condition(condition, data) is True

    def test_rsi_greater_equal(self):
        condition = {"type": "indicator", "name": "RSI", "period": 14, "operator": "greater_equal", "value": 70}
        data = {"indicators": {"RSI_14": 72.0}}
        assert evaluate_indicator_condition(condition, data) is True

    def test_macd_without_period(self):
        condition = {"type": "indicator", "name": "MACD", "operator": "greater_than", "value": 0}
        data = {"indicators": {"MACD": 0.005}}
        assert evaluate_indicator_condition(condition, data) is True

    def test_indicator_not_found(self):
        condition = {"type": "indicator", "name": "RSI", "period": 7, "operator": "less_than", "value": 30}
        data = {"indicators": {"MACD": 0.005}}
        assert evaluate_indicator_condition(condition, data) is False


class TestSMCEvaluator:
    def test_fvg_bullish_found(self):
        condition = {"type": "smc", "name": "FVG", "direction": "bullish", "lookback": 5}
        data = {"smc": {"FVG": [{"direction": "bullish", "candle_index": -2}]}}
        assert evaluate_smc_condition(condition, data) is True

    def test_fvg_wrong_direction(self):
        condition = {"type": "smc", "name": "FVG", "direction": "bearish", "lookback": 5}
        data = {"smc": {"FVG": [{"direction": "bullish", "candle_index": -2}]}}
        assert evaluate_smc_condition(condition, data) is False

    def test_fvg_out_of_lookback(self):
        condition = {"type": "smc", "name": "FVG", "direction": "bullish", "lookback": 3}
        data = {"smc": {"FVG": [{"direction": "bullish", "candle_index": -10}]}}
        assert evaluate_smc_condition(condition, data) is False

    def test_no_smc_data(self):
        condition = {"type": "smc", "name": "OB"}
        data = {"smc": {}}
        assert evaluate_smc_condition(condition, data) is False


class TestCompoundEvaluator:
    def test_and_all_true(self):
        condition = {
            "operator": "and",
            "conditions": [
                {"type": "price", "operator": "greater_than", "value": 1900.0},
                {"type": "indicator", "name": "RSI", "period": 14, "operator": "less_than", "value": 30},
            ],
        }
        data = {"close": 2000.0, "indicators": {"RSI_14": 25.0}}
        assert evaluate_condition(condition, data) is True

    def test_and_one_false(self):
        condition = {
            "operator": "and",
            "conditions": [
                {"type": "price", "operator": "greater_than", "value": 1900.0},
                {"type": "indicator", "name": "RSI", "period": 14, "operator": "less_than", "value": 30},
            ],
        }
        data = {"close": 2000.0, "indicators": {"RSI_14": 45.0}}
        assert evaluate_condition(condition, data) is False

    def test_or_one_true(self):
        condition = {
            "operator": "or",
            "conditions": [
                {"type": "price", "operator": "greater_than", "value": 3000.0},
                {"type": "indicator", "name": "RSI", "period": 14, "operator": "less_than", "value": 30},
            ],
        }
        data = {"close": 2000.0, "indicators": {"RSI_14": 25.0}}
        assert evaluate_condition(condition, data) is True

    def test_or_all_false(self):
        condition = {
            "operator": "or",
            "conditions": [
                {"type": "price", "operator": "greater_than", "value": 3000.0},
                {"type": "indicator", "name": "RSI", "period": 14, "operator": "greater_than", "value": 80},
            ],
        }
        data = {"close": 2000.0, "indicators": {"RSI_14": 50.0}}
        assert evaluate_condition(condition, data) is False

    def test_nested_compound(self):
        condition = {
            "operator": "and",
            "conditions": [
                {"type": "price", "operator": "greater_than", "value": 1900.0},
                {
                    "operator": "or",
                    "conditions": [
                        {"type": "indicator", "name": "RSI", "period": 14, "operator": "less_than", "value": 30},
                        {"type": "smc", "name": "FVG", "direction": "bullish", "lookback": 5},
                    ],
                },
            ],
        }
        data = {
            "close": 2000.0,
            "indicators": {"RSI_14": 40.0},
            "smc": {"FVG": [{"direction": "bullish", "candle_index": -2}]},
        }
        assert evaluate_condition(condition, data) is True
