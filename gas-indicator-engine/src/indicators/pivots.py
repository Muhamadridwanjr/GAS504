import numpy as np
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("PIVOTS")
def get_pivots(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    # Shift high, low, close by 1 index to get the previous period's values
    n = len(data["close"])
    if n < 2:
        zero_arr = np.zeros(n)
        return {"p": zero_arr, "r1": zero_arr, "s1": zero_arr, "r2": zero_arr, "s2": zero_arr, "r3": zero_arr, "s3": zero_arr}
        
    high_prev = np.empty_like(data["high"])
    low_prev = np.empty_like(data["low"])
    close_prev = np.empty_like(data["close"])
    
    high_prev[1:] = data["high"][:-1]
    low_prev[1:] = data["low"][:-1]
    close_prev[1:] = data["close"][:-1]
    
    # Pad the first element with NaN
    high_prev[0] = np.nan
    low_prev[0] = np.nan
    close_prev[0] = np.nan
    
    p = (high_prev + low_prev + close_prev) / 3.0
    r1 = (2 * p) - low_prev
    s1 = (2 * p) - high_prev
    r2 = p + (high_prev - low_prev)
    s2 = p - (high_prev - low_prev)
    r3 = high_prev + 2 * (p - low_prev)
    s3 = low_prev - 2 * (high_prev - p)
    
    return {
        "pivot": p,
        "r1": r1, "s1": s1,
        "r2": r2, "s2": s2,
        "r3": r3, "s3": s3
    }
