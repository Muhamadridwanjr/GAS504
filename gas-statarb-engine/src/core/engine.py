from typing import Dict, Any
from src.core.pair_manager import pair_manager
from src.clients.market_data import market_client
from src.core.calculator import evaluate_spread
from src.config import settings
from src.lib.logger import logger

class StatArbEngine:
    async def generate_signal(self, pair: str, req_lookback: int = None, req_threshold: float = None) -> Dict[str, Any]:
        """
        Retrieves parameters and current prices, calculates Z-Score, and generates Signal.
        """
        threshold = req_threshold if req_threshold is not None else settings.zscore_threshold
        
        # 1. Get Params (beta, mean, std) from Cache
        params = await pair_manager.get_pair_params(pair)
        if not params:
            return self._build_neutral_response(pair, "Params not available")
            
        sym_x, sym_y = params['symbol_x'], params['symbol_y']
        
        # 2. Get latest Prices
        price_x = await market_client.get_latest_price(sym_x)
        price_y = await market_client.get_latest_price(sym_y)
        
        if price_x is None or price_y is None:
            return self._build_neutral_response(pair, "Prices not available")
            
        # 3. Calculate spread and z-score
        spread, zscore = evaluate_spread(
            price_y, 
            price_x, 
            beta=params['beta'], 
            mean=params['mean_spread'], 
            std=params['std_spread']
        )
        
        # 4. Generate Signal
        signal = "NEUTRAL"
        confidence = 0.5
        
        # Logic: If zscore > threshold, spread is too wide. Sell Y, Buy X (SHORT_SPREAD)
        # If zscore < -threshold, spread is too narrow. Buy Y, Sell X (LONG_SPREAD)
        if zscore > threshold:
            signal = "SHORT_SPREAD"
            confidence = min(0.95, 0.5 + (abs(zscore) - threshold) / 5.0)
        elif zscore < -threshold:
            signal = "LONG_SPREAD"
            confidence = min(0.95, 0.5 + (abs(zscore) - threshold) / 5.0)
            
        return {
            "pair": pair,
            "signal": signal,
            "zscore": round(zscore, 4),
            "hedge_ratio": round(params['beta'], 4),
            "spread": round(spread, 4),
            "entry_prices": {
                sym_x: price_x,
                sym_y: price_y
            },
            "confidence": round(confidence, 4)
        }
        
    def _build_neutral_response(self, pair: str, reason: str) -> Dict[str, Any]:
        logger.warning(f"Returning neutral for {pair}: {reason}")
        return {
            "pair": pair,
            "signal": "NEUTRAL",
            "zscore": 0.0,
            "hedge_ratio": 1.0,
            "spread": 0.0,
            "entry_prices": {},
            "confidence": 0.5
        }

engine = StatArbEngine()
