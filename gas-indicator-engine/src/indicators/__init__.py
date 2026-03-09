from src.indicators.registry import INDICATOR_REGISTRY, register_indicator, calculate_all

# Pre-load all indicator modules so they register themselves
from src.indicators import moving_averages
from src.indicators import momentum
from src.indicators import volume
from src.indicators import volatility
from src.indicators import trend
from src.indicators import statistical
from src.indicators import hilbert
from src.indicators import candlestick
from src.indicators import custom
from src.indicators import pivots
from src.indicators import demand_zone

__all__ = ["calculate_all", "register_indicator", "INDICATOR_REGISTRY"]
