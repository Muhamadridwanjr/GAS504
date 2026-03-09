from typing import Dict, List
from src.lib.logger import get_logger

logger = get_logger(__name__)

class BiasCalculator:
    """Determines bias (BULLISH/BEARISH/NEUTRAL) for a target asset based on correlated assets."""

    @staticmethod
    def calculate_bias(target: str, correlation_row: Dict[str, float], latest_returns: Dict[str, float], threshold: float = 0.7) -> dict:
        """
        Given correlation data for `target`, and latest returns for all assets,
        determine whether the cross-asset signal is bullish, bearish, or neutral.
        """
        factors = []
        bullish_score = 0.0
        bearish_score = 0.0

        for symbol, corr_val in correlation_row.items():
            if symbol == target:
                continue
            if abs(corr_val) < threshold:
                continue  # Ignore weakly correlated assets

            latest_ret = latest_returns.get(symbol, 0.0)
            if latest_ret == 0:
                continue

            if corr_val > 0:
                # Positive correlation: same direction
                contribution = "bullish" if latest_ret > 0 else "bearish"
            else:
                # Negative correlation: opposite direction
                contribution = "bearish" if latest_ret > 0 else "bullish"

            if contribution == "bullish":
                bullish_score += abs(corr_val)
            else:
                bearish_score += abs(corr_val)

            factors.append({
                "symbol": symbol,
                "correlation": round(corr_val, 4),
                "return": round(latest_ret, 6),
                "contribution": contribution
            })

        total = bullish_score + bearish_score
        if total == 0:
            bias = "NEUTRAL"
            confidence = 0.0
        elif bullish_score > bearish_score:
            bias = "BULLISH"
            confidence = round(bullish_score / total, 2)
        else:
            bias = "BEARISH"
            confidence = round(bearish_score / total, 2)

        return {
            "symbol": target,
            "bias": bias,
            "confidence": confidence,
            "factors": factors
        }
