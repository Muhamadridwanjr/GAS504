"""Unit tests for condition_evaluator — no network, no DB.
Uses actual ScreenerCondition schema: type, name, period, operator, value, direction
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.api.models import ScreenerCondition
from src.core.condition_evaluator import evaluate_condition, evaluate_all

# When period is None -> key = name (e.g. "RSI")
# When period is set  -> key = f"{name}_{period}" (e.g. "EMA_20" when name=EMA, period=20)
INDICATORS = {
    "RSI": 35.5,
    "EMA": 1910.0,        # name only (no period)
    "EMA_20": 1910.0,     # name_period format for period=20
    "EMA_50": 1920.0,     # name_period format for period=50
}
SMC = {
    "trend": "bearish",
    "order_blocks": [{"direction": "bearish", "price": 1920.0}],
}


def ind_cond(name, operator, value, period=None):
    return ScreenerCondition(type="indicator", name=name, operator=operator, value=value, period=period)


def smc_cond(name, direction=None):
    return ScreenerCondition(type="smc", name=name, direction=direction)


class TestEvaluateConditionIndicator:
    def test_less_than_true(self):
        c = ind_cond("RSI", "<", 40)
        assert evaluate_condition(c, INDICATORS, SMC) is True

    def test_less_than_false(self):
        c = ind_cond("RSI", "<", 30)
        assert evaluate_condition(c, INDICATORS, SMC) is False

    def test_greater_than_no_period(self):
        # Without period, key = "EMA"
        c = ind_cond("EMA", ">", 1900.0)
        assert evaluate_condition(c, INDICATORS, SMC) is True

    def test_greater_than_with_period(self):
        # With period=20, key = "EMA_20"
        c = ind_cond("EMA", ">", 1900.0, period=20)
        assert evaluate_condition(c, INDICATORS, SMC) is True

    def test_equal(self):
        c = ind_cond("RSI", "==", 35.5)
        assert evaluate_condition(c, INDICATORS, SMC) is True

    def test_not_equal(self):
        c = ind_cond("RSI", "!=", 99.0)
        assert evaluate_condition(c, INDICATORS, SMC) is True

    def test_missing_indicator_returns_false(self):
        c = ind_cond("NONEXISTENT", ">", 0)
        assert evaluate_condition(c, INDICATORS, SMC) is False


class TestEvaluateConditionSMC:
    def test_smc_order_block_bearish_found(self):
        c = smc_cond("order_block", direction="bearish")
        assert evaluate_condition(c, INDICATORS, SMC) is True

    def test_smc_order_block_bullish_not_found(self):
        c = smc_cond("order_block", direction="bullish")
        assert evaluate_condition(c, INDICATORS, SMC) is False

    def test_smc_no_direction(self):
        c = smc_cond("order_block")
        assert evaluate_condition(c, INDICATORS, SMC) is True

    def test_unknown_type_returns_false(self):
        c = ScreenerCondition(type="UNKNOWN", name="RSI")
        assert evaluate_condition(c, INDICATORS, SMC) is False


class TestEvaluateAll:
    def test_and_all_pass(self):
        conds = [ind_cond("RSI", "<", 40), ind_cond("EMA", ">", 1900.0)]
        assert evaluate_all(conds, INDICATORS, SMC, logic="AND") is True

    def test_and_one_fails(self):
        conds = [ind_cond("RSI", "<", 40), ind_cond("RSI", ">", 50)]
        assert evaluate_all(conds, INDICATORS, SMC, logic="AND") is False

    def test_or_one_passes(self):
        conds = [ind_cond("RSI", ">", 50), ind_cond("RSI", "<", 40)]
        assert evaluate_all(conds, INDICATORS, SMC, logic="OR") is True

    def test_or_all_fail(self):
        conds = [ind_cond("RSI", ">", 50), ind_cond("RSI", ">", 80)]
        assert evaluate_all(conds, INDICATORS, SMC, logic="OR") is False

    def test_empty_conditions(self):
        assert evaluate_all([], INDICATORS, SMC, logic="AND") is True
        assert evaluate_all([], INDICATORS, SMC, logic="OR") is True
