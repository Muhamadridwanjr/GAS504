"""
Evaluator Engine for gas-alert-engine.

Evaluates user-defined alert conditions against market data.
Supports: price alerts, indicator-based alerts, SMC markers, and compound AND/OR logic.

Security: No `eval()` or `exec()`. All evaluation uses explicit operator mapping.
"""

from typing import Any
from src.lib.logger import logger


# ── Comparison operators ─────────────────────────────────────

OPERATORS = {
    "greater_than": lambda a, b: a > b,
    "less_than": lambda a, b: a < b,
    "greater_equal": lambda a, b: a >= b,
    "less_equal": lambda a, b: a <= b,
    "equals": lambda a, b: a == b,
    "not_equals": lambda a, b: a != b,
    "cross_above": lambda current, prev, target: prev <= target and current > target,
    "cross_below": lambda current, prev, target: prev >= target and current < target,
}


def _safe_float(val: Any) -> float | None:
    """Coerce a value to float safely."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


# ── Price evaluator ──────────────────────────────────────────

def evaluate_price_condition(condition: dict, market_data: dict) -> bool:
    """
    Evaluate a price-based condition.

    condition example:
        {"type": "price", "operator": "cross_above", "value": 2000.0}

    market_data must include:
        {"close": 2001.5, "prev_close": 1999.8}
    """
    operator = condition.get("operator", "")
    target = _safe_float(condition.get("value"))
    if target is None:
        logger.warning(f"Price condition missing value: {condition}")
        return False

    close = _safe_float(market_data.get("close"))
    if close is None:
        return False

    if operator in ("cross_above", "cross_below"):
        prev = _safe_float(market_data.get("prev_close", market_data.get("open")))
        if prev is None:
            return False
        fn = OPERATORS.get(operator)
        return fn(close, prev, target) if fn else False

    fn = OPERATORS.get(operator)
    return fn(close, target) if fn else False


# ── Indicator evaluator ─────────────────────────────────────

def evaluate_indicator_condition(condition: dict, market_data: dict) -> bool:
    """
    Evaluate an indicator-based condition.

    condition example:
        {"type": "indicator", "name": "RSI", "period": 14, "operator": "less_than", "value": 30}

    market_data must include indicators:
        {"indicators": {"RSI_14": 28.5, "MACD": 0.002, ...}}
    """
    indicator_name = condition.get("name", "").upper()
    period = condition.get("period")
    operator = condition.get("operator", "")
    target = _safe_float(condition.get("value"))
    if target is None:
        return False

    indicators = market_data.get("indicators", {})

    # Build key: e.g. "RSI_14" or just "MACD"
    key = f"{indicator_name}_{period}" if period else indicator_name
    current_value = _safe_float(indicators.get(key))
    if current_value is None:
        # Try without period
        current_value = _safe_float(indicators.get(indicator_name))
    if current_value is None:
        logger.debug(f"Indicator {key} not found in market data")
        return False

    fn = OPERATORS.get(operator)
    return fn(current_value, target) if fn else False


# ── SMC evaluator ────────────────────────────────────────────

def evaluate_smc_condition(condition: dict, market_data: dict) -> bool:
    """
    Evaluate a Smart Money Concept condition.

    condition example:
        {"type": "smc", "name": "FVG", "direction": "bullish", "lookback": 5}

    market_data must include smc data:
        {"smc": {"FVG": [{"direction": "bullish", "candle_index": -2}, ...]}}
    """
    smc_name = condition.get("name", "").upper()
    direction = condition.get("direction")
    lookback = condition.get("lookback", 10)

    smc_data = market_data.get("smc", {})
    markers = smc_data.get(smc_name, [])

    if not markers:
        return False

    for marker in markers:
        # Check direction filter
        if direction and marker.get("direction") != direction:
            continue
        # Check lookback (candle_index should be within -lookback..0)
        idx = marker.get("candle_index", -999)
        if abs(idx) <= lookback:
            return True

    return False


# ── Compound evaluator (AND / OR) ───────────────────────────

def evaluate_condition(condition: dict, market_data: dict) -> bool:
    """
    Main entry point – evaluates any condition recursively.

    Compound example:
        {
          "operator": "and",
          "conditions": [
            {"type": "price", ...},
            {"type": "indicator", ...}
          ]
        }
    """
    # Compound condition
    if "conditions" in condition:
        sub_conditions = condition["conditions"]
        op = condition.get("operator", "and").lower()

        if op == "and":
            return all(evaluate_condition(c, market_data) for c in sub_conditions)
        elif op == "or":
            return any(evaluate_condition(c, market_data) for c in sub_conditions)
        else:
            logger.warning(f"Unknown compound operator: {op}")
            return False

    # Single condition
    cond_type = condition.get("type", "").lower()

    if cond_type == "price":
        return evaluate_price_condition(condition, market_data)
    elif cond_type == "indicator":
        return evaluate_indicator_condition(condition, market_data)
    elif cond_type == "smc":
        return evaluate_smc_condition(condition, market_data)
    else:
        logger.warning(f"Unknown condition type: {cond_type}")
        return False
