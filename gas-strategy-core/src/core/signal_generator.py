from typing import Dict, Any, Optional
from src.models.strategy import StopLossConfig, TakeProfitConfig

class SignalGenerator:
    @staticmethod
    def generate(action: str, data: Dict[str, Any], sl_config: Optional[StopLossConfig], tp_config: Optional[TakeProfitConfig]) -> Dict[str, Any]:
        """Generate final trading signal based on the evaluated action and config."""
        
        # Default empty signal
        signal = {
            "action": action,
            "entry_price": data.get("price", {}).get("close", 0.0),
            "stop_loss": 0.0,
            "take_profit": 0.0,
            "confidence": 0.8,
            "metadata": {}
        }
        
        if action == "NEUTRAL":
            return signal
            
        current_price = signal["entry_price"]
        
        # Basic SL implementation based on offsets
        if sl_config:
            # Handle new syntax (atr_multiplier) vs old syntax (offset_points)
            offset = sl_config.offset_points if sl_config.offset_points else (sl_config.atr_multiplier * 10 if sl_config.atr_multiplier else 0)
            if action == "BUY":
                signal["stop_loss"] = current_price - offset
            elif action == "SELL":
                signal["stop_loss"] = current_price + offset
                
        # Basic TP implementation based on RR or multi-target
        if tp_config and sl_config:
            if tp_config.risk_reward_ratio:
                risk = abs(current_price - signal["stop_loss"]) if signal["stop_loss"] > 0 else 10
                if action == "BUY":
                    signal["take_profit"] = current_price + (risk * tp_config.risk_reward_ratio)
                elif action == "SELL":
                    signal["take_profit"] = current_price - (risk * tp_config.risk_reward_ratio)
            elif tp_config.type == "multi_target" and tp_config.targets:
                # If multi-target, we return the primary target (or format out a list)
                # For simplicity here, just grab the first level as a baseline or calculate an avg
                # A real system would pass back an array of targets to the orchestrator.
                signal["take_profit"] = tp_config.targets[0].level
                signal["metadata"]["multi_targets"] = [{"level": t.level, "portion": t.portion} for t in tp_config.targets]

        return signal
