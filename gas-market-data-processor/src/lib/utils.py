def parse_timeframe_to_seconds(tf: str) -> int:
    """Konversi string timeframe menjadi detik."""
    tf = tf.upper()
    if tf.startswith("M") and tf != "MN":
        return int(tf[1:]) * 60
    elif tf.startswith("H"):
        return int(tf[1:]) * 3600
    elif tf.startswith("D"):
        return int(tf[1:]) * 86400
    elif tf.startswith("W"):
        return int(tf[1:]) * 604800
    elif tf == "MN":
        return 30 * 86400
    return 60  # Default 1 Minute fallback

def get_candle_start_time(timestamp: int, tf_seconds: int) -> int:
    """Mendapatkan timestamp awal dari candle saat ini."""
    return timestamp - (timestamp % tf_seconds)
