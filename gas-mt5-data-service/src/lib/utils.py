def timeframe_to_seconds(timeframe: str) -> int:
    """Convert MT5 timeframe string to seconds"""
    mapping = {
        "M1": 60,
        "M5": 300,
        "M15": 900,
        "M30": 1800,
        "H1": 3600,
        "H4": 14400,
        "D1": 86400,
        "W1": 604800,
        "MN": 2592000 # Approx 30 days
    }
    return mapping.get(timeframe, 3600)  # Default to H1 if not found
