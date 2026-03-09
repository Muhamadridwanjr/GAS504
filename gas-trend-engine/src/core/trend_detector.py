from src.core.breakout import evaluate_breakout
from src.core.ma_cross import evaluate_ma_cross
from src.cache.redis_cache import cache
from src.lib.logger import get_logger

logger = get_logger(__name__)

class TrendDetector:
    def __init__(self):
        pass

    async def get_features(self, symbol: str, timeframe: str) -> dict:
        """Mock feature fetch. Replace with real feature-engine call."""
        logger.info(f"Mocking feature fetch for {symbol} {timeframe}")
        return {
            "close": 2005.5,
            "highest_20": 2005.5,
            "lowest_20": 1980.0,
            "ema_10": 2002.0,
            "ema_30": 1995.0,
            "adx": 28.5,
            "atr": 15.0
        }

    async def detect(self, symbol: str, timeframe: str, method: str = "both",
                     breakout_period: int = 20, ma_fast: int = 10, ma_slow: int = 30,
                     adx_threshold: int = 25) -> dict:

        cache_key = f"trend:{symbol}:{timeframe}:{method}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        features = await self.get_features(symbol, timeframe)
        
        results = []
        if method in ("breakout", "both"):
            results.append(evaluate_breakout(features, period=breakout_period))
        if method in ("ma_cross", "both"):
            results.append(evaluate_ma_cross(features, ma_fast_period=ma_fast, ma_slow_period=ma_slow))

        # Combine signals if both methods used
        if len(results) == 2:
            if results[0]["signal"] == results[1]["signal"] and results[0]["signal"] != "NEUTRAL":
                final_signal = results[0]["signal"]
                final_strength = round((results[0]["strength"] + results[1]["strength"]) / 2 + 0.1, 2)
                final_strength = min(final_strength, 0.99)
            elif results[0]["strength"] > results[1]["strength"]:
                final_signal = results[0]["signal"]
                final_strength = results[0]["strength"]
            else:
                final_signal = results[1]["signal"]
                final_strength = results[1]["strength"]
            combined_method = "both"
            combined_details = {**results[0].get("details", {}), **results[1].get("details", {})}
        else:
            final_signal = results[0]["signal"]
            final_strength = results[0]["strength"]
            combined_method = results[0]["method"]
            combined_details = results[0].get("details", {})

        # Compute SL/TP based on ATR
        atr = features.get("atr", 15.0)
        close = features.get("close", 0)
        if final_signal == "BUY":
            sl = round(close - atr * 1.5, 3)
            tp = round(close + atr * 3, 3)
        elif final_signal == "SELL":
            sl = round(close + atr * 1.5, 3)
            tp = round(close - atr * 3, 3)
        else:
            sl = 0
            tp = 0

        response = {
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": final_signal,
            "strength": final_strength,
            "method": combined_method,
            "entry_price": close,
            "stop_loss": sl,
            "take_profit": tp,
            "details": combined_details
        }

        await cache.set(cache_key, response)
        return response
