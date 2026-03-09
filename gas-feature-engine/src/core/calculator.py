import typing
import pandas as pd
import numpy as np
import ta

def compute_features(df: pd.DataFrame, requested_features: typing.List[str]) -> pd.DataFrame:
    """
    Computes a list of requested financial features for the given OHLC dataframe.
    Expected columns: time, open, high, low, close, volume (or varying).
    Returns a pandas dataframe containing at least 'time' plus the requested features.
    """
    
    # We always need time as reference
    out_cols = ['time']
    if 'time' not in df.columns:
        # If index is datetime, make it a column
        if pd.api.types.is_datetime64_any_dtype(df.index):
            df['time'] = df.index.astype(int) // 10**9
        else:
            raise ValueError("Input dataframe must have 'time' column or datetime index.")
            
    df = df.sort_values('time').copy()
    result = df[['time']].copy()

    # Define standard series
    close = df.get('close')
    high = df.get('high')
    low = df.get('low')
    
    if close is None:
        return result

    for f in requested_features:
        f = f.lower()
        try:
            # RETURNS
            if f == 'return_1':
                result[f] = close.pct_change(1)
            elif f == 'return_5':
                result[f] = close.pct_change(5)
            elif f == 'log_return_1':
                result[f] = np.log(close / close.shift(1))
            
            # VOLATILITY
            elif f.startswith('volatility_'):
                period = int(f.split('_')[1])
                # Daily volatility approx
                result[f] = close.pct_change(1).rolling(period).std()
            elif f.startswith('atr_') and (high is not None and low is not None):
                period = int(f.split('_')[1])
                result[f] = ta.volatility.average_true_range(high, low, close, window=period)
                
            # ZSCORE
            elif f.startswith('zscore_'):
                period = int(f.split('_')[1])
                sma = close.rolling(period).mean()
                std = close.rolling(period).std()
                result[f] = (close - sma) / std
                
            # MOMENTUM
            elif f.startswith('rsi_'):
                period = int(f.split('_')[1])
                result[f] = ta.momentum.rsi(close, window=period)
            elif f == 'macd':
                result[f] = ta.trend.macd_diff(close)
                
            # MOVING AVERAGES
            elif f.startswith('sma_'):
                period = int(f.split('_')[1])
                result[f] = close.rolling(period).mean()
            elif f.startswith('ema_'):
                period = int(f.split('_')[1])
                result[f] = ta.trend.ema_indicator(close, window=period)
            
            # VOLUME
            elif f == 'volume_ratio' and 'volume' in df:
                vol = df['volume']
                sma_vol = vol.rolling(20).mean()
                result[f] = vol / sma_vol

        except Exception as e:
            # If calculation fails (e.g. not enough data), just insert NaN
            result[f] = np.nan

    # Drop rows that don't have all required features computed if needed 
    # Or just return as is (NaNs included at the start for rolling features)
    return result
