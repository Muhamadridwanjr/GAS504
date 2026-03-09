import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
import numpy as np
import pandas as pd
from typing import Tuple

def test_cointegration(y: pd.Series, x: pd.Series) -> Tuple[float, float, float]:
    """
    Test cointegration using Engle-Granger two-step method.
    Returns: (coint_t, p_value, crit_val_1pct)
    """
    try:
        coint_t, p_value, crit_value = ts.coint(y, x)
        # return t-stat, p-value, and the 1% critical value
        return coint_t, p_value, crit_value[0]
    except Exception as e:
        return 0.0, 1.0, 0.0

def calculate_ols_hedge_ratio(y: pd.Series, x: pd.Series) -> float:
    """
    Calculates hedge ratio (beta) using Ordinary Least Squares: y = alpha + beta * x
    """
    try:
        x_with_const = sm.add_constant(x)
        model = sm.OLS(y, x_with_const).fit()
        return model.params.iloc[1] # beta
    except Exception as e:
        return 1.0 # Default if fails

def evaluate_spread(y_price: float, x_price: float, beta: float, mean: float, std: float) -> Tuple[float, float]:
    """
    Returns (spread, zscore)
    """
    spread = y_price - beta * x_price
    
    if std == 0:
        return spread, 0.0
        
    zscore = (spread - mean) / std
    return spread, zscore
