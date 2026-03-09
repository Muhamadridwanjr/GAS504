import numpy as np
from typing import Dict, List, Any, Callable
from src.lib.logger import log

# Registry map: indicator_name -> calculation_function
# Function signature: func(data_dict: Dict[str, np.ndarray], **kwargs) -> Dict[str, np.ndarray]
# The returned dict contains the names of the output lines (e.g., "macd", "macdsignal", "macdhist") and their numpy array values.
INDICATOR_REGISTRY: Dict[str, Callable] = {}

def register_indicator(name: str):
    """Decorator to register an indicator calculation function."""
    def decorator(func: Callable):
        INDICATOR_REGISTRY[name.upper()] = func
        return func
    return decorator

def calculate_all(data: List[Dict[str, Any]], indicators_req: List[Any]) -> List[Dict[str, Any]]:
    """Process multiple indicators for given OHLC data using the registry."""
    if not data:
        return []
    
    # Convert list of dicts to numpy arrays for fast calculation via TA-Lib
    arr_data = {
        "open": np.array([float(x.get("open", 0)) for x in data], dtype=np.float64),
        "high": np.array([float(x.get("high", 0)) for x in data], dtype=np.float64),
        "low": np.array([float(x.get("low", 0)) for x in data], dtype=np.float64),
        "close": np.array([float(x.get("close", 0)) for x in data], dtype=np.float64),
        "volume": np.array([float(x.get("volume", 0)) for x in data], dtype=np.float64),
    }
    timestamps = [x.get("time", 0) for x in data]
    
    results = []
    
    for req in indicators_req:
        name = req.name.upper()
        if name not in INDICATOR_REGISTRY:
            log.warning(f"Indicator {name} not found in registry. Skipping.")
            continue
            
        func = INDICATOR_REGISTRY[name]
        params = req.params or {}
        
        # Determine periods to run. If indicator has no period, we default to [0].
        periods = req.periods if req.periods else [0]
        
        for period in periods:
            # Pass period in params if > 0
            call_params = params.copy()
            if period > 0:
                call_params["timeperiod"] = period
            
            try:
                # Format of returned value: {"line_name": np.ndarray, ...}
                calc_results = func(arr_data, **call_params)
                
                # We could have multiple lines per indicator (like MACD) or just one.
                # If the returned dictionary has multiple keys, we return them separately or together?
                # The GRPC/REST schema allows one `values` array per IndicatorResult.
                # However, for MACD, we might need to return separate IndicatorResults for 'MACD', 'MACDSIGNAL', 'MACDHIST'
                # Or we can pack it in one if the schema supports it. The protobuf defined earlier:
                # `repeated double values = 3;` (1D array)
                # This means each line should be its own IndicatorResult. For example: name="MACD_SIGNAL"
                
                for line_name, values_arr in calc_results.items():
                    # clean nan
                    clean_values = [float(v) if not np.isnan(v) else 0.0 for v in values_arr]
                    
                    res_name = name if line_name == "default" else f"{name}_{line_name.upper()}"
                    
                    results.append({
                        "name": res_name,
                        "period": period,
                        "values": clean_values,
                        "timestamps": timestamps
                    })
            except Exception as e:
                log.error(f"Error calculating {name} with period {period}: {e}")
                
    return results
