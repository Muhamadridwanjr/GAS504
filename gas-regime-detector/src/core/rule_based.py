from typing import Tuple, Dict, Any

class RuleBasedDetector:
    def __init__(self):
        # Default thresholds
        self.adx_trend_thr = 25
        self.adx_range_thr = 20
        # More complex rules can be defined here

    def detect(self, features: Dict[str, float]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Takes a dictionary of features and returns (regime_name, confidence, details_dict)
        """
        adx = features.get('adx_14', 0)
        volatility = features.get('volatility_20', 0)
        
        details = {
            "adx_used": adx,
            "volatility_used": volatility
        }

        if adx > self.adx_trend_thr:
            # High confidence if ADX is very high, otherwise moderate
            confidence = min(0.95, 0.7 + (adx - self.adx_trend_thr) / 100)
            return "TRENDING", round(confidence, 2), details
            
        elif adx < self.adx_range_thr:
            # Low ADX typically indicates a ranging market
            confidence = min(0.85, 0.6 + (self.adx_range_thr - adx) / 50)
            return "RANGING", round(confidence, 2), details
            
        else:
            return "TRANSITION", 0.5, details
