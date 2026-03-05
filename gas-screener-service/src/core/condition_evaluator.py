"""
Condition evaluator for screener results.
"""
from __future__ import annotations
from typing import Any

from src.api.models import ScreenerCondition
from src.lib.logger import get_logger

logger = get_logger(__name__)


OPERATORS = {
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}


def evaluate_condition(
    condition: ScreenerCondition,
    indicators: dict[str, Any],
    smc: dict[str, Any],
) -> bool:
    """
    Evaluate a single condition against indicator / SMC data.
    """
    if condition.type == "indicator":
        key = f"{condition.name}_{condition.period}" if condition.period else condition.name
        val = indicators.get(key)
        if val is None:
            return False
        op_fn = OPERATORS.get(condition.operator or ">")
        if op_fn is None:
            return False
        return op_fn(float(val), float(condition.value or 0))

    elif condition.type == "smc":
        name_lower = condition.name.lower()
        # Look for matching SMC detections
        items = smc.get(f"{name_lower}s", smc.get(name_lower, []))
        if not items:
            return False
        if condition.direction:
            items = [
                i for i in items
                if isinstance(i, dict) and i.get("direction") == condition.direction
            ]
        return len(items) > 0

    return False


def evaluate_all(
    conditions: list[ScreenerCondition],
    indicators: dict[str, Any],
    smc: dict[str, Any],
    logic: str = "AND",
) -> bool:
    """Evaluate all conditions with AND/OR logic."""
    results = [evaluate_condition(c, indicators, smc) for c in conditions]
    if not results:
        return True
    if logic.upper() == "AND":
        return all(results)
    return any(results)
