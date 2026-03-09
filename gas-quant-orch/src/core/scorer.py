from typing import Dict, Any, Tuple
from src.config import settings
from src.lib.logger import logger

class Scorer:
    def calculate_score(self, regime_data: Dict, pattern_data: Dict, statarb_data: Dict) -> Tuple[float, float, str]:
        """
        Aggregate results and return (score, confidence, final_signal).
        """
        total_score = 0.0
        total_weight = 0.0
        total_conf = 0.0
        
        regime = regime_data.get("regime", "RANGING")
        r_conf = regime_data.get("confidence", 0.5)
        
        # We adjust weights based on regime
        w_pattern = settings.weight_pattern
        w_statarb = settings.weight_statarb
        
        if regime == "TRENDING":
            w_pattern *= 1.5
            w_statarb *= 0.5
        elif regime == "RANGING":
            w_pattern *= 0.8
            w_statarb *= 1.5
            
        # Pattern Score
        p_dir = pattern_data.get("expected_direction", "NEUTRAL")
        p_conf = pattern_data.get("confidence", 0.0)
        p_val = 1.0 if p_dir == "BUY" else (-1.0 if p_dir == "SELL" else 0.0)
        
        total_score += (p_val * p_conf) * w_pattern
        total_weight += w_pattern
        total_conf += p_conf * w_pattern
        
        # StatArb Score
        s_dir = statarb_data.get("signal", "NEUTRAL")
        s_conf = statarb_data.get("confidence", 0.0)
        s_val = 1.0 if s_dir in ["BUY", "LONG_SPREAD"] else (-1.0 if s_dir in ["SELL", "SHORT_SPREAD"] else 0.0)
        
        total_score += (s_val * s_conf) * w_statarb
        total_weight += w_statarb
        total_conf += s_conf * w_statarb
        
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        final_conf = total_conf / total_weight if total_weight > 0 else 0.5
        
        signal = "NEUTRAL"
        if final_score >= settings.signal_threshold:
            signal = "BUY"
        elif final_score <= -settings.signal_threshold:
            signal = "SELL"
            
        return final_score, final_conf, signal

scorer = Scorer()
