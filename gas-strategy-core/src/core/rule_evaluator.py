from typing import Dict, Any, List
from src.models.strategy import StrategyCondition

def evaluate_indicator_condition(cond: StrategyCondition, data: Dict[str, Any]) -> bool:
    indicators = data.get("indicators", {})
    val = indicators.get(f"{cond.name}_{cond.period}") or indicators.get(cond.name)
    
    if val is None:
        # Fallback for checking raw price like close
        val = data.get("price", {}).get(cond.name)
        if val is None:
            return False
            
    # For specialized operators like bullish_divergence or expand
    if cond.operator in ["bullish_divergence", "reversal_up", "price_above", "volatility_expand"]:
        return True # Stubs for these complex patterns that need historical lookbacks
        
    if cond.operator is None and cond.value is None:
        return True
        
    cv = cond.value
    if isinstance(cv, str):
        cv = data.get("price", {}).get(cv) or data.get("indicators", {}).get(cv)
        if cv is None:
            return False

    if cond.operator == "less_than":
        return val < cv
    elif cond.operator == "greater_than":
        return val > cv
    elif cond.operator == "equal":
        return val == cv
    return False

def evaluate_smc_condition(cond: StrategyCondition, data: Dict[str, Any]) -> bool:
    smc_data = data.get("smc", {})
    markers = smc_data.get(cond.name.lower() + "s", []) if cond.name else []
    
    if cond.direction:
        markers = [m for m in markers if m.get("direction") == cond.direction]
        
    if cond.status:
        markers = [m for m in markers if m.get("status") == cond.status]
        
    if cond.lookback and len(markers) > 0:
        return True
    return len(markers) > 0

def evaluate_market_structure(cond: StrategyCondition, data: Dict[str, Any]) -> bool:
    """Evaluate structure conditions like BOS or CHoCH from smc data."""
    smc_data = data.get("smc", {})
    markers = smc_data.get(cond.name.lower()) or smc_data.get(cond.name.lower() + "s", [])
    if cond.direction:
        markers = [m for m in markers if m.get("direction") == cond.direction]
    return len(markers) > 0
    
def evaluate_macro(cond: StrategyCondition, data: Dict[str, Any]) -> bool:
    """Evaluate macro correlation condition placeholder."""
    return True

def evaluate_price_condition(cond: StrategyCondition, data: Dict[str, Any]) -> bool:
    """Evaluate simple expressions like 'close > open'"""
    price_data = data.get("price", {})
    if not cond.condition:
        return False
    # Safe eval limited to price keys
    allowed_locals = {k: v for k, v in price_data.items()}
    try:
        return eval(cond.condition, {"__builtins__": {}}, allowed_locals)
    except Exception:
        return False

class RuleEvaluator:
    @staticmethod
    def evaluate(conditions: List[StrategyCondition], data: Dict[str, Any], operator: str = "AND") -> bool:
        if not conditions:
            return False
            
        results = []
        for cond in conditions:
            if cond.type == "indicator":
                results.append(evaluate_indicator_condition(cond, data))
            elif cond.type == "smc":
                results.append(evaluate_smc_condition(cond, data))
            elif cond.type == "price":
                results.append(evaluate_price_condition(cond, data))
            elif cond.type == "market_structure":
                results.append(evaluate_market_structure(cond, data))
            elif cond.type == "macro":
                results.append(evaluate_macro(cond, data))
            else:
                results.append(False)
                
        if operator.upper() == "AND":
            return all(results)
        elif operator.upper() == "OR":
            return any(results)
            
        return False
