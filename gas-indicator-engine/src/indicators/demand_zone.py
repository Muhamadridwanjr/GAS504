import numpy as np
import pandas as pd
from typing import Dict
from src.indicators.registry import register_indicator

@register_indicator("DEMAND_ZONE")
def get_demand_zone(data: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]:
    """
    Returns proxy for a demand zone. 
    By default uses a rolling 20-period minimum of the Lows as the major support / demand level.
    """
    period = kwargs.get("timeperiod", 20)
    lows = pd.Series(data["low"])
    demand_level = lows.rolling(window=period).min()
    
    return {"default": demand_level.values}
