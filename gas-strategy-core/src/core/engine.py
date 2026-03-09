from typing import Dict, Any, Optional
from src.core.loader import StrategyLoader
from src.core.rule_evaluator import RuleEvaluator
from src.core.signal_generator import SignalGenerator
import logging

logger = logging.getLogger(__name__)

def evaluate(strategy_name: str, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main entry point for gas-strategy-core. Evaluate strategy on incoming data.
    """
    try:
        # Load Strategy
        strategy = StrategyLoader.load(strategy_name)
    except FileNotFoundError:
        logger.error(f"Strategy {strategy_name} not found")
        return {"action": "ERROR", "metadata": {"error": "Strategy not found"}}

    # Validate conditions
    # ALM structure uses separate categorizations. Use the aggregated property
    is_triggered = RuleEvaluator.evaluate(
        conditions=strategy.all_conditions, 
        data=data, 
        operator=strategy.combination
    )

    if not is_triggered:
        return {
            "action": "NEUTRAL",
            "entry_price": data.get("price", {}).get("close", 0.0),
            "metadata": {"strategy_name": strategy.name, "message": "Conditions not met"}
        }

    # Evaluate Sell Mirror Logic
    # If the strategy specifies `invert_all: true` for sell_conditions and we fired a BUY,
    # theoretically a separate process would invert. For gas-strategy-core, the orchestrator
    # usually manages long/short state, but we return the primary action.
    action = strategy.action
    
    # Generate Signal
    signal = SignalGenerator.generate(
        action=action,
        data=data,
        sl_config=strategy.stop_loss,
        tp_config=strategy.take_profit
    )
    
    signal["metadata"]["strategy_name"] = strategy.name
    signal["metadata"]["message"] = "Conditions met"
    signal["metadata"]["version"] = strategy.version
    
    return signal
