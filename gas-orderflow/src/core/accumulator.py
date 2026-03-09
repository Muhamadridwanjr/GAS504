from typing import Dict, List
from collections import defaultdict
import time
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

class TickAccumulator:
    """Accumulates incoming ticks per symbol and computes order flow metrics."""

    def __init__(self):
        # In-memory store per symbol
        self._data: Dict[str, dict] = {}

    def _init_symbol(self, symbol: str):
        self._data[symbol] = {
            "buy_volume": 0.0,
            "sell_volume": 0.0,
            "delta": 0.0,
            "cumulative_delta": 0.0,
            "tick_count": 0,
            "last_price": 0.0,
            "timestamp": int(time.time()),
            "volume_by_price": defaultdict(float)
        }

    def ingest_tick(self, symbol: str, price: float, volume: float, side: str):
        if symbol not in self._data:
            self._init_symbol(symbol)

        d = self._data[symbol]
        d["tick_count"] += 1
        d["last_price"] = price
        d["timestamp"] = int(time.time())

        if side.lower() == "buy":
            d["buy_volume"] += volume
        else:
            d["sell_volume"] += volume

        d["delta"] = d["buy_volume"] - d["sell_volume"]
        d["cumulative_delta"] += (volume if side.lower() == "buy" else -volume)

        # Track volume by rounded price level for liquidity zone detection
        price_level = round(price, 1)
        d["volume_by_price"][price_level] += volume

    def get_metrics(self, symbol: str) -> dict:
        if symbol not in self._data:
            self._init_symbol(symbol)
        d = self._data[symbol]
        total_vol = d["buy_volume"] + d["sell_volume"]
        imbalance = (d["buy_volume"] - d["sell_volume"]) / total_vol if total_vol > 0 else 0

        pressure = "NEUTRAL"
        if d["delta"] > settings.DELTA_THRESHOLD and imbalance > settings.IMBALANCE_THRESHOLD:
            pressure = "BUY"
        elif d["delta"] < -settings.DELTA_THRESHOLD and imbalance < -settings.IMBALANCE_THRESHOLD:
            pressure = "SELL"

        return {
            "symbol": symbol,
            "timestamp": d["timestamp"],
            "delta": round(d["delta"], 2),
            "cumulative_delta": round(d["cumulative_delta"], 2),
            "buy_volume": round(d["buy_volume"], 2),
            "sell_volume": round(d["sell_volume"], 2),
            "imbalance": round(imbalance, 4),
            "pressure": pressure,
            "tick_count": d["tick_count"]
        }

    def get_liquidity_zones(self, symbol: str, min_volume: float = 500) -> list:
        if symbol not in self._data:
            return []
        zones = []
        vbp = self._data[symbol]["volume_by_price"]
        for price_level, vol in sorted(vbp.items(), key=lambda x: x[1], reverse=True):
            if vol >= min_volume:
                zones.append({
                    "price": price_level,
                    "volume": round(vol, 2),
                    "type": "support" if price_level < self._data[symbol]["last_price"] else "resistance"
                })
            if len(zones) >= 10:
                break
        return zones

    def reset_symbol(self, symbol: str):
        if symbol in self._data:
            self._init_symbol(symbol)

accumulator = TickAccumulator()
