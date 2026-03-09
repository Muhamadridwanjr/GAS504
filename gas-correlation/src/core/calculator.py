import numpy as np
import pandas as pd
from typing import Dict, List
from src.lib.logger import get_logger

logger = get_logger(__name__)

class CorrelationCalculator:
    """Calculates rolling Pearson correlation between asset return series."""

    @staticmethod
    def compute_correlation_matrix(returns: Dict[str, List[float]], window: int = 20) -> Dict[str, Dict[str, float]]:
        """
        Given a dictionary of {symbol: [returns...]}, compute the pairwise
        rolling Pearson correlation using the last `window` data points.
        Returns a nested dict of {symbolA: {symbolB: correlation, ...}, ...}
        """
        df = pd.DataFrame(returns)
        # Use only the last `window` rows
        df = df.tail(window)

        if len(df) < 3:
            logger.warning("Not enough data to compute correlation.")
            return {}

        corr_matrix = df.corr(method="pearson")
        result = {}
        for sym in corr_matrix.columns:
            result[sym] = {}
            for other in corr_matrix.columns:
                result[sym][other] = round(float(corr_matrix.loc[sym, other]), 4)
        return result

    @staticmethod
    def get_pair_correlation(returns: Dict[str, List[float]], sym1: str, sym2: str, window: int = 20) -> float:
        if sym1 not in returns or sym2 not in returns:
            return 0.0
        s1 = pd.Series(returns[sym1]).tail(window)
        s2 = pd.Series(returns[sym2]).tail(window)
        if len(s1) < 3 or len(s2) < 3:
            return 0.0
        return round(float(s1.corr(s2)), 4)
