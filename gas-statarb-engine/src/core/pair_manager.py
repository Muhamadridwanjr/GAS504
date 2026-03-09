import pandas as pd
from typing import List, Dict, Any
from src.config import settings
from src.lib.logger import logger
from src.cache.redis_cache import cache
from src.clients.market_data import market_client
from src.core.calculator import test_cointegration, calculate_ols_hedge_ratio

class PairManager:
    def __init__(self):
        self.pairs = settings.parsed_pairs # e.g. [["XAUUSD", "DXY"]]
        
    async def initialize_pairs(self):
        """
        Calculates initial parameters (beta, mean, std) for default pairs and caches them.
        """
        for pair_symbols in self.pairs:
            pair_name = f"{pair_symbols[0]}_{pair_symbols[1]}"
            await self.update_pair(pair_name, pair_symbols[0], pair_symbols[1])
            
    async def get_pair_params(self, pair_name: str) -> Dict[str, Any]:
        """
        Gets parameters from cache, returns dict.
        """
        key = f"statarb:pair:{pair_name}"
        params = await cache.get(key)
        # Handle case where pair isn't in cache yet
        if not params:
            parts = pair_name.split("_")
            if len(parts) == 2:
                params = await self.update_pair(pair_name, parts[0], parts[1])
        return params or {}

    async def update_pair(self, pair_name: str, sym_x: str, sym_y: str) -> Dict[str, Any]:
        """
        Fetch history, calculate beta, mean, std for the spread, and store in Redis.
        X represents the independent variable, Y is dependent.
        """
        logger.info(f"Updating parameters for {pair_name}")
        df_x = await market_client.get_ohlc(sym_x, limit=settings.lookback_period + 100) # Fetch extra for stats
        df_y = await market_client.get_ohlc(sym_y, limit=settings.lookback_period + 100)
        
        if df_x is None or df_y is None or df_x.empty or df_y.empty:
            logger.warning(f"Could not update parameters for {pair_name}: missing market data")
            return {}

        # Merge on time
        merged = pd.merge(df_y[['time', 'close']], df_x[['time', 'close']], on='time', suffixes=('_y', '_x')).dropna()
        if len(merged) < min(10, settings.lookback_period):
            logger.warning(f"Not enough overlapping data for {pair_name}")
            return {}
            
        y_series = merged['close_y']
        x_series = merged['close_x']
        
        # Calculate params
        beta = calculate_ols_hedge_ratio(y_series, x_series)
        spread_series = y_series - beta * x_series
        
        # Usually need to check cointegration roughly here
        # coint_t, p_val, crit = test_cointegration(y_series, x_series)
        
        lookback = settings.lookback_period
        recent_spread = spread_series.tail(lookback)
        
        mean_spread = float(recent_spread.mean())
        std_spread = float(recent_spread.std())
        
        params = {
            "pair": pair_name,
            "symbol_x": sym_x,
            "symbol_y": sym_y,
            "beta": beta,
            "mean_spread": mean_spread,
            "std_spread": std_spread
        }
        
        # Cache for updates
        await cache.set(f"statarb:pair:{pair_name}", params, ttl=86400) # Keep for a day
        return params

pair_manager = PairManager()
