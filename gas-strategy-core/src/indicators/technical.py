import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

def compute_indicators(candles: List[Dict], indicators: List[str] = None) -> Dict[str, Any]:
    """
    Compute technical indicators from OHLCV candle data.
    candles: list of dicts with keys: time, open, high, low, close, volume
             sorted oldest-first (ascending time)
    Returns dict of indicator values and signals.
    """
    if not candles or len(candles) < 20:
        return {"error": "Insufficient candle data", "candle_count": len(candles)}

    if indicators is None:
        indicators = ["RSI", "MACD", "ADX", "BB", "EMA"]

    df = pd.DataFrame(candles)
    df = df.sort_values("time").reset_index(drop=True)
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    result = {}
    current_price = float(df["close"].iloc[-1])
    result["current_price"] = current_price
    result["candle_count"] = len(df)

    try:
        import pandas_ta as ta

        if "RSI" in indicators:
            rsi_series = ta.rsi(df["close"], length=14)
            if rsi_series is not None and not rsi_series.empty:
                rsi_val = float(rsi_series.iloc[-1])
                result["RSI"] = {
                    "value": round(rsi_val, 2),
                    "signal": "OVERSOLD" if rsi_val < 30 else "OVERBOUGHT" if rsi_val > 70 else "NEUTRAL",
                    "action": "BUY" if rsi_val < 30 else "SELL" if rsi_val > 70 else "HOLD",
                }

        if "MACD" in indicators:
            macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
            if macd is not None and not macd.empty:
                macd_val = float(macd["MACD_12_26_9"].iloc[-1])
                signal_val = float(macd["MACDs_12_26_9"].iloc[-1])
                hist_val = float(macd["MACDh_12_26_9"].iloc[-1])
                result["MACD"] = {
                    "macd": round(macd_val, 5),
                    "signal_line": round(signal_val, 5),
                    "histogram": round(hist_val, 5),
                    "signal": "BULLISH" if macd_val > signal_val else "BEARISH",
                    "action": "BUY" if macd_val > signal_val and hist_val > 0 else "SELL" if macd_val < signal_val and hist_val < 0 else "WAIT",
                }

        if "ADX" in indicators:
            adx = ta.adx(df["high"], df["low"], df["close"], length=14)
            if adx is not None and not adx.empty:
                adx_val = float(adx["ADX_14"].iloc[-1])
                dmp = float(adx["DMP_14"].iloc[-1])
                dmn = float(adx["DMN_14"].iloc[-1])
                result["ADX"] = {
                    "value": round(adx_val, 2),
                    "dmp": round(dmp, 2),
                    "dmn": round(dmn, 2),
                    "signal": "STRONG TREND" if adx_val > 25 else "WEAK/RANGING",
                    "direction": "BULLISH" if dmp > dmn else "BEARISH",
                    "strength": "STRONG" if adx_val > 40 else "MODERATE" if adx_val > 25 else "WEAK",
                }

        if "BB" in indicators:
            bb = ta.bbands(df["close"], length=20, std=2)
            if bb is not None and not bb.empty:
                upper = float(bb["BBU_20_2.0"].iloc[-1])
                middle = float(bb["BBM_20_2.0"].iloc[-1])
                lower = float(bb["BBL_20_2.0"].iloc[-1])
                bandwidth = float(bb["BBB_20_2.0"].iloc[-1]) if "BBB_20_2.0" in bb else 0
                position = (
                    "UPPER" if current_price > middle + (upper - middle) * 0.5
                    else "LOWER" if current_price < middle - (middle - lower) * 0.5
                    else "MIDDLE"
                )
                result["BB"] = {
                    "upper": round(upper, 5),
                    "middle": round(middle, 5),
                    "lower": round(lower, 5),
                    "bandwidth": round(bandwidth, 4),
                    "position": position,
                    "signal": "OVERSOLD" if current_price < lower else "OVERBOUGHT" if current_price > upper else "NEUTRAL",
                }

        if "EMA" in indicators:
            ema20 = ta.ema(df["close"], length=20)
            ema50 = ta.ema(df["close"], length=50)
            ema200 = ta.ema(df["close"], length=200) if len(df) >= 200 else None
            e20 = float(ema20.iloc[-1]) if ema20 is not None else None
            e50 = float(ema50.iloc[-1]) if ema50 is not None else None
            e200 = float(ema200.iloc[-1]) if ema200 is not None else None
            ema_signal = "BULLISH" if (e20 and e50 and e20 > e50) else "BEARISH"
            result["EMA"] = {
                "ema20": round(e20, 5) if e20 else None,
                "ema50": round(e50, 5) if e50 else None,
                "ema200": round(e200, 5) if e200 else None,
                "signal": ema_signal,
                "price_vs_ema20": "ABOVE" if e20 and current_price > e20 else "BELOW",
            }

    except ImportError:
        # Full manual fallback using only numpy/pandas — no external TA library needed
        closes = df["close"].values.astype(float)
        highs  = df["high"].values.astype(float)
        lows   = df["low"].values.astype(float)
        n = len(closes)

        def _ema_arr(arr, period):
            k = 2.0 / (period + 1)
            out = np.empty(len(arr))
            out[:period] = np.mean(arr[:period])
            for i in range(period, len(arr)):
                out[i] = arr[i] * k + out[i-1] * (1 - k)
            return out

        def _rma(arr, period):
            """Wilder's smoothed MA used in RSI/ADX."""
            out = np.empty(len(arr))
            out[:period] = np.mean(arr[:period])
            for i in range(period, len(arr)):
                out[i] = (out[i-1] * (period - 1) + arr[i]) / period
            return out

        # ── RSI ──────────────────────────────────────────────────────────────
        if "RSI" in indicators and n >= 15:
            diffs = np.diff(closes)
            gains = np.where(diffs > 0, diffs, 0.0)
            losses = np.where(diffs < 0, -diffs, 0.0)
            avg_g = _rma(gains, 14)
            avg_l = _rma(losses, 14)
            rs = avg_g[-1] / avg_l[-1] if avg_l[-1] != 0 else 100.0
            rsi_val = round(100 - (100 / (1 + rs)), 2)
            result["RSI"] = {
                "value": rsi_val,
                "signal": "OVERSOLD" if rsi_val < 30 else "OVERBOUGHT" if rsi_val > 70 else "NEUTRAL",
                "action": "BUY" if rsi_val < 30 else "SELL" if rsi_val > 70 else "HOLD",
            }

        # ── MACD ─────────────────────────────────────────────────────────────
        if "MACD" in indicators and n >= 35:
            ema12 = _ema_arr(closes, 12)
            ema26 = _ema_arr(closes, 26)
            macd_line = ema12 - ema26
            signal_line = _ema_arr(macd_line, 9)
            hist = macd_line - signal_line
            mv, sv, hv = macd_line[-1], signal_line[-1], hist[-1]
            result["MACD"] = {
                "macd": round(mv, 5),
                "signal_line": round(sv, 5),
                "histogram": round(hv, 5),
                "signal": "BULLISH" if mv > sv else "BEARISH",
                "action": "BUY" if mv > sv and hv > 0 else "SELL" if mv < sv and hv < 0 else "WAIT",
            }

        # ── EMA ──────────────────────────────────────────────────────────────
        if "EMA" in indicators and n >= 20:
            e20 = round(_ema_arr(closes, 20)[-1], 5)
            e50 = round(_ema_arr(closes, 50)[-1], 5) if n >= 50 else None
            e200 = round(_ema_arr(closes, 200)[-1], 5) if n >= 200 else None
            ema_sig = "BULLISH" if (e50 and e20 > e50) else "BEARISH"
            result["EMA"] = {
                "ema20": e20, "ema50": e50, "ema200": e200,
                "signal": ema_sig,
                "price_vs_ema20": "ABOVE" if current_price > e20 else "BELOW",
                "action": "BUY" if ema_sig == "BULLISH" and current_price > e20 else "SELL" if ema_sig == "BEARISH" and current_price < e20 else "HOLD",
            }

        # ── Bollinger Bands ───────────────────────────────────────────────────
        if "BB" in indicators and n >= 20:
            sma20 = np.mean(closes[-20:])
            std20 = np.std(closes[-20:], ddof=1)
            upper = round(sma20 + 2 * std20, 5)
            middle = round(sma20, 5)
            lower = round(sma20 - 2 * std20, 5)
            bw = round((upper - lower) / middle * 100, 4) if middle != 0 else 0
            pos = ("UPPER" if current_price > middle + (upper - middle) * 0.5
                   else "LOWER" if current_price < middle - (middle - lower) * 0.5
                   else "MIDDLE")
            result["BB"] = {
                "upper": upper, "middle": middle, "lower": lower,
                "bandwidth": bw, "position": pos,
                "signal": "OVERSOLD" if current_price < lower else "OVERBOUGHT" if current_price > upper else "NEUTRAL",
                "action": "BUY" if current_price < lower else "SELL" if current_price > upper else "HOLD",
            }

        # ── ADX ──────────────────────────────────────────────────────────────
        if "ADX" in indicators and n >= 20:
            p = 14
            tr = np.maximum(highs[1:] - lows[1:],
                            np.maximum(np.abs(highs[1:] - closes[:-1]),
                                       np.abs(lows[1:] - closes[:-1])))
            dmp_raw = np.where(((highs[1:] - highs[:-1]) > (lows[:-1] - lows[1:])) &
                               ((highs[1:] - highs[:-1]) > 0), highs[1:] - highs[:-1], 0.0)
            dmn_raw = np.where(((lows[:-1] - lows[1:]) > (highs[1:] - highs[:-1])) &
                               ((lows[:-1] - lows[1:]) > 0), lows[:-1] - lows[1:], 0.0)
            atr14 = _rma(tr, p)
            dmp14 = _rma(dmp_raw, p)
            dmn14 = _rma(dmn_raw, p)
            di_plus = 100 * dmp14 / (atr14 + 1e-10)
            di_minus = 100 * dmn14 / (atr14 + 1e-10)
            dx = 100 * np.abs(di_plus - di_minus) / (di_plus + di_minus + 1e-10)
            adx_arr = _rma(dx, p)
            adx_val = round(adx_arr[-1], 2)
            dp, dn = round(di_plus[-1], 2), round(di_minus[-1], 2)
            result["ADX"] = {
                "value": adx_val, "dmp": dp, "dmn": dn,
                "signal": "STRONG TREND" if adx_val > 25 else "WEAK/RANGING",
                "direction": "BULLISH" if dp > dn else "BEARISH",
                "strength": "STRONG" if adx_val > 40 else "MODERATE" if adx_val > 25 else "WEAK",
            }

    # Overall recommendation based on available indicators
    buy_signals = 0
    sell_signals = 0
    total = 0
    for key in ["RSI", "MACD", "EMA", "BB"]:
        if key in result and isinstance(result[key], dict):
            action = result[key].get("action", result[key].get("signal", ""))
            if "BUY" in action or "BULLISH" in action or "OVERSOLD" in action:
                buy_signals += 1
            elif "SELL" in action or "BEARISH" in action or "OVERBOUGHT" in action:
                sell_signals += 1
            total += 1

    if total > 0:
        if buy_signals > sell_signals:
            rec = "BUY"
            conf = int((buy_signals / total) * 100)
        elif sell_signals > buy_signals:
            rec = "SELL"
            conf = int((sell_signals / total) * 100)
        else:
            rec = "NEUTRAL"
            conf = 50
    else:
        rec = "NEUTRAL"
        conf = 0

    result["recommendation"] = rec
    result["confidence"] = conf

    return result


def compute_indicators_only(pair: str, timeframe: str, candles: list) -> dict:
    """
    FAST compute level — indicators only, no SMC engine call, no LLM.
    Returns same shape as compute_indicators() plus current_price, confluence_score,
    setup_type so the caller (technical_analysis endpoint) doesn't need to branch.
    Runs synchronously (~5ms) — no network I/O.
    """
    result = compute_indicators(candles)
    # Add fields that _build_feature_summary normally provides
    result.setdefault("current_price", 0)
    result.setdefault("confluence_score", result.get("confidence", 0))
    result.setdefault("setup_type", "indicator-only")
    result.setdefault("SMC", None)
    return result
