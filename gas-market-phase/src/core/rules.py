from typing import Tuple

def detect_phase(features: dict) -> Tuple[str, float, dict]:
    """
    Applies Livermore-inspired rules to determine market phase.
    Returns: (Phase, Confidence, Details)
    """
    price = features.get('price', 0)
    ema50 = features.get('ema50', 0)
    adx = features.get('adx', 0)
    volume_ratio = features.get('volume_ratio', 1.0)
    low_20 = features.get('low_20', 0)
    high_20 = features.get('high_20', 0)
    
    price_vs_ema50 = "above" if price > ema50 else "below"
    breakout_detected = False

    phase = "SIDEWAYS"
    confidence = 0.5
    
    # Markup: Strong uptrend, high volume, ADX > 25
    if price > ema50 and adx > 25 and volume_ratio > 1.1:
        phase = "MARKUP"
        confidence = min(0.7 + (adx - 25) / 100, 0.99)
        if price >= high_20:
            breakout_detected = True
            
    # Markdown: Strong downtrend, high volume, ADX > 25
    elif price < ema50 and adx > 25 and volume_ratio > 1.1:
        phase = "MARKDOWN"
        confidence = min(0.7 + (adx - 25) / 100, 0.99)
        if price <= low_20:
            breakout_detected = True
            
    # Accumulation / Distribution: Range bound but high relative volume
    elif volume_ratio > 1.2 and abs(price - ema50) / ema50 < 0.01:
        # Simplified logic: If price is near the lower end of the recent range, it's accumulation
        if price < (low_20 + high_20) / 2:
            phase = "ACCUMULATION"
            confidence = 0.65
        else:
            phase = "DISTRIBUTION"
            confidence = 0.65
            
    details = {
        "price_vs_ema50": price_vs_ema50,
        "adx": round(adx, 2),
        "volume_ratio": round(volume_ratio, 2),
        "breakout_detected": breakout_detected
    }
    
    return phase, round(confidence, 2), details
