import numpy as np
import pandas as pd
from typing import List, Dict, Any

def candles_to_df(candles: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(candles)
    df["datetime"] = pd.to_datetime(df["time"], unit="s")
    df = df.set_index("datetime").sort_index()
    for col in ["open","high","low","close","volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def calc_rsi(close: pd.Series, period: int = 14) -> float:
    if len(close) < period + 1:
        return 50.0
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi.iloc[-1]), 2)

def calc_macd(close: pd.Series, fast=12, slow=26, signal=9) -> Dict:
    if len(close) < slow + signal:
        return {"macd": 0, "signal": 0, "histogram": 0, "cross": "neutral"}
    ema_fast = close.ewm(span=fast).mean()
    ema_slow = close.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    cross = "neutral"
    if len(histogram) >= 2:
        if histogram.iloc[-1] > 0 and histogram.iloc[-2] <= 0:
            cross = "bullish_cross"
        elif histogram.iloc[-1] < 0 and histogram.iloc[-2] >= 0:
            cross = "bearish_cross"
        elif histogram.iloc[-1] > 0:
            cross = "bullish"
        elif histogram.iloc[-1] < 0:
            cross = "bearish"
    return {
        "macd": round(float(macd_line.iloc[-1]), 4),
        "signal": round(float(signal_line.iloc[-1]), 4),
        "histogram": round(float(histogram.iloc[-1]), 4),
        "cross": cross,
    }

def calc_ema(close: pd.Series, period: int) -> float:
    if len(close) < period:
        return float(close.iloc[-1]) if len(close) > 0 else 0
    return round(float(close.ewm(span=period).mean().iloc[-1]), 2)

def calc_bb(close: pd.Series, period: int = 20, std: float = 2.0) -> Dict:
    if len(close) < period:
        return {"upper": 0, "middle": 0, "lower": 0, "width": 0, "position": 0.5}
    mid = close.rolling(period).mean()
    band = close.rolling(period).std() * std
    upper = mid + band
    lower = mid - band
    last_close = float(close.iloc[-1])
    last_upper = float(upper.iloc[-1])
    last_lower = float(lower.iloc[-1])
    last_mid = float(mid.iloc[-1])
    width = (last_upper - last_lower) / last_mid if last_mid != 0 else 0
    position = (last_close - last_lower) / (last_upper - last_lower) if (last_upper - last_lower) != 0 else 0.5
    return {
        "upper": round(last_upper, 2),
        "middle": round(last_mid, 2),
        "lower": round(last_lower, 2),
        "width": round(width, 4),
        "position": round(position, 3),
    }

def calc_stoch(high: pd.Series, low: pd.Series, close: pd.Series, k=14, d=3) -> Dict:
    if len(close) < k:
        return {"k": 50, "d": 50, "signal": "neutral"}
    lowest_low = low.rolling(k).min()
    highest_high = high.rolling(k).max()
    stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
    stoch_d = stoch_k.rolling(d).mean()
    k_val = round(float(stoch_k.iloc[-1]), 2)
    d_val = round(float(stoch_d.iloc[-1]), 2)
    signal = "neutral"
    if k_val < 20 and d_val < 20:
        signal = "oversold"
    elif k_val > 80 and d_val > 80:
        signal = "overbought"
    elif k_val > d_val:
        signal = "bullish"
    elif k_val < d_val:
        signal = "bearish"
    return {"k": k_val, "d": d_val, "signal": signal}

def calc_vwap(df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0
    typical = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (typical * df["volume"]).cumsum() / df["volume"].cumsum().replace(0, 1e-10)
    return round(float(vwap.iloc[-1]), 2)

def calc_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
    if len(close) < period + 1:
        return 0
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)
    return round(float(tr.rolling(period).mean().iloc[-1]), 2)

def volume_analysis(df: pd.DataFrame) -> Dict:
    if len(df) < 5:
        return {"avg_vol": 0, "rel_vol": 1.0, "trend": "normal"}
    avg_vol = df["volume"].rolling(20).mean().iloc[-1]
    last_vol = df["volume"].iloc[-1]
    rel_vol = round(float(last_vol / avg_vol), 2) if avg_vol > 0 else 1.0
    trend = "high" if rel_vol > 1.5 else "low" if rel_vol < 0.5 else "normal"
    return {"avg_vol": int(avg_vol), "rel_vol": rel_vol, "trend": trend}

def build_signal(indicators: Dict, current_price: float) -> Dict:
    """Build trading signal from indicator confluence."""
    score = 50  # neutral base
    signals = []

    rsi = indicators.get("rsi", 50)
    macd = indicators.get("macd", {})
    bb = indicators.get("bollinger", {})
    stoch = indicators.get("stochastic", {})
    ema9 = indicators.get("ema9", current_price)
    ema21 = indicators.get("ema21", current_price)
    ema50 = indicators.get("ema50", current_price)

    # RSI
    if rsi < 30:
        score += 15; signals.append("RSI oversold (strong buy)")
    elif rsi < 40:
        score += 8; signals.append("RSI approaching oversold")
    elif rsi > 70:
        score -= 15; signals.append("RSI overbought (strong sell)")
    elif rsi > 60:
        score -= 8; signals.append("RSI approaching overbought")

    # MACD
    cross = macd.get("cross", "neutral")
    if cross == "bullish_cross":
        score += 20; signals.append("MACD bullish crossover")
    elif cross == "bearish_cross":
        score -= 20; signals.append("MACD bearish crossover")
    elif cross == "bullish":
        score += 8; signals.append("MACD positive momentum")
    elif cross == "bearish":
        score -= 8; signals.append("MACD negative momentum")

    # EMA trend
    if current_price > ema21 > ema50:
        score += 10; signals.append("Price above EMA21 > EMA50 (uptrend)")
    elif current_price < ema21 < ema50:
        score -= 10; signals.append("Price below EMA21 < EMA50 (downtrend)")
    if ema9 > ema21:
        score += 5; signals.append("EMA9 > EMA21 (short-term bullish)")
    elif ema9 < ema21:
        score -= 5; signals.append("EMA9 < EMA21 (short-term bearish)")

    # Bollinger
    bb_pos = bb.get("position", 0.5)
    if bb_pos < 0.1:
        score += 10; signals.append("Price near lower Bollinger Band")
    elif bb_pos > 0.9:
        score -= 10; signals.append("Price near upper Bollinger Band")

    # Stochastic
    stoch_sig = stoch.get("signal", "neutral")
    if stoch_sig == "oversold":
        score += 10; signals.append("Stochastic oversold")
    elif stoch_sig == "overbought":
        score -= 10; signals.append("Stochastic overbought")

    score = max(0, min(100, score))

    if score >= 70:
        action = "BUY"
        strength = "Strong" if score >= 85 else "Moderate"
        color = "green"
    elif score <= 30:
        action = "SELL"
        strength = "Strong" if score <= 15 else "Moderate"
        color = "red"
    else:
        action = "HOLD"
        strength = "Neutral"
        color = "yellow"

    return {
        "action": action,
        "strength": strength,
        "score": score,
        "color": color,
        "signals": signals[:5],
    }

def full_analysis(candles: List[Dict]) -> Dict:
    """Run all indicators on candle list."""
    if len(candles) < 20:
        return {"error": "need_more_candles"}
    df = candles_to_df(candles)
    close = df["close"]
    high = df["high"]
    low = df["low"]
    current = float(close.iloc[-1])

    ema9  = calc_ema(close, 9)
    ema21 = calc_ema(close, 21)
    ema50 = calc_ema(close, 50)
    ema200= calc_ema(close, 200)

    indicators = {
        "rsi": calc_rsi(close),
        "macd": calc_macd(close),
        "bollinger": calc_bb(close),
        "stochastic": calc_stoch(high, low, close),
        "ema9": ema9,
        "ema21": ema21,
        "ema50": ema50,
        "ema200": ema200,
        "vwap": calc_vwap(df),
        "atr": calc_atr(high, low, close),
        "volume": volume_analysis(df),
    }

    trend = "uptrend" if current > ema21 and ema21 > ema50 else \
            "downtrend" if current < ema21 and ema21 < ema50 else "sideways"

    support = round(float(low.rolling(20).min().iloc[-1]), 2)
    resistance = round(float(high.rolling(20).max().iloc[-1]), 2)

    signal = build_signal(indicators, current)

    return {
        "indicators": indicators,
        "trend": trend,
        "support": support,
        "resistance": resistance,
        "signal": signal,
        "candle_count": len(candles),
        "last_price": current,
    }
