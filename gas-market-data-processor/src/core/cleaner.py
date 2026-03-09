from src.lib.logger import get_logger

logger = get_logger(__name__)

def clean_tick(price: float, volume: float, timestamp: int, last_timestamp: int = 0) -> bool:
    """Validates tick data."""
    if price <= 0:
        logger.warning(f"Invalid price {price} at {timestamp}")
        return False
    if volume < 0:
        logger.warning(f"Invalid volume {volume} at {timestamp}")
        return False
    if timestamp < last_timestamp:
        logger.warning(f"Out of order tick: {timestamp} < {last_timestamp}")
        # In a real engine, we might reorder them, but typically we drop or flag late ticks
        return False
    return True

def clean_ohlc(open: float, high: float, low: float, close: float, volume: float) -> bool:
    """Validates OHLC data."""
    if any(x <= 0 for x in [open, high, low, close]):
        return False
    if volume < 0:
        return False
    if high < low or high < open or high < close:
        return False
    if low > high or low > open or low > close:
        return False
    return True
