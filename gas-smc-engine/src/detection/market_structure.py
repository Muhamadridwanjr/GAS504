"""
Market Structure Detector — Real SMC Implementation
Detects: Swing Points (HH, HL, LH, LL), BOS, CHoCH
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any


def _find_swing_points(df: pd.DataFrame, lookback: int = 3) -> pd.DataFrame:
    """Identify swing highs and swing lows using a rolling window."""
    df = df.copy()
    df["swing_high"] = False
    df["swing_low"] = False
    n = len(df)

    for i in range(lookback, n - lookback):
        window_highs = df["high"].iloc[i - lookback: i + lookback + 1]
        window_lows  = df["low"].iloc[i - lookback: i + lookback + 1]
        if df["high"].iloc[i] == window_highs.max():
            df.at[df.index[i], "swing_high"] = True
        if df["low"].iloc[i] == window_lows.min():
            df.at[df.index[i], "swing_low"] = True

    return df


class MarketStructureDetector:
    def detect(self, candles: List[Dict], params: dict = None) -> Dict[str, Any]:
        if not candles or len(candles) < 20:
            return {
                "bias": "NEUTRAL",
                "structure_type": "INSUFFICIENT_DATA",
                "swing_points": [],
                "bos": [],
                "choch": [],
                "last_swing_high": None,
                "last_swing_low": None,
            }

        df = pd.DataFrame(candles)
        df = df.sort_values("time").reset_index(drop=True)
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)

        lookback = max(3, min(5, len(df) // 20))
        df = _find_swing_points(df, lookback)

        swing_high_rows = df[df["swing_high"]].copy()
        swing_low_rows  = df[df["swing_low"]].copy()

        sh_prices = swing_high_rows["high"].tolist()
        sl_prices = swing_low_rows["low"].tolist()
        sh_times  = swing_high_rows["time"].tolist()
        sl_times  = swing_low_rows["time"].tolist()

        current_price = float(df["close"].iloc[-1])

        # ── Determine bias from last two swing highs and lows ──────────────────
        bias = "NEUTRAL"
        structure_type = "NEUTRAL"

        if len(sh_prices) >= 2 and len(sl_prices) >= 2:
            last_sh, prev_sh = sh_prices[-1], sh_prices[-2]
            last_sl, prev_sl = sl_prices[-1], sl_prices[-2]

            hh = last_sh > prev_sh
            hl = last_sl > prev_sl
            lh = last_sh < prev_sh
            ll = last_sl < prev_sl

            if hh and hl:
                bias = "BULLISH"
                structure_type = "HH-HL"
            elif lh and ll:
                bias = "BEARISH"
                structure_type = "LH-LL"
            elif hh and ll:
                structure_type = "EXPANDING"
            elif lh and hl:
                structure_type = "CONTRACTING"
            else:
                structure_type = "RANGING"

        # ── BOS Detection ──────────────────────────────────────────────────────
        bos_list = []
        choch_list = []

        if len(sh_prices) >= 2 and len(sl_prices) >= 2:
            last_sh  = sh_prices[-1]
            prev_sh  = sh_prices[-2]
            last_sl  = sl_prices[-1]
            prev_sl  = sl_prices[-2]

            # Recent candles (last 10)
            recent_high = float(df["high"].tail(10).max())
            recent_low  = float(df["low"].tail(10).min())

            # Bullish BOS: price broke above previous swing high (continuation)
            if recent_high > prev_sh and bias == "BULLISH":
                bos_list.append({
                    "type": "BULLISH_BOS",
                    "level": round(prev_sh, 5),
                    "confirmed": current_price > prev_sh,
                    "description": "Break of Structure — Bullish continuation confirmed",
                })

            # Bearish BOS: price broke below previous swing low (continuation)
            if recent_low < prev_sl and bias == "BEARISH":
                bos_list.append({
                    "type": "BEARISH_BOS",
                    "level": round(prev_sl, 5),
                    "confirmed": current_price < prev_sl,
                    "description": "Break of Structure — Bearish continuation confirmed",
                })

            # CHoCH Bullish: price was bearish but breaks above last swing high
            if bias == "BEARISH" and current_price > last_sh:
                choch_list.append({
                    "type": "BULLISH_CHOCH",
                    "level": round(last_sh, 5),
                    "description": "Change of Character — Potential bullish reversal (watch for OB/FVG entry)",
                })

            # CHoCH Bearish: price was bullish but breaks below last swing low
            if bias == "BULLISH" and current_price < last_sl:
                choch_list.append({
                    "type": "BEARISH_CHOCH",
                    "level": round(last_sl, 5),
                    "description": "Change of Character — Potential bearish reversal (watch for OB/FVG entry)",
                })

        # ── Build swing point list (last 8 sorted by time) ────────────────────
        swing_points = []
        for price, t in zip(sh_prices[-5:], sh_times[-5:]):
            swing_points.append({"type": "HIGH", "price": round(float(price), 5), "time": int(t)})
        for price, t in zip(sl_prices[-5:], sl_times[-5:]):
            swing_points.append({"type": "LOW", "price": round(float(price), 5), "time": int(t)})
        swing_points.sort(key=lambda x: x["time"])

        return {
            "bias": bias,
            "structure_type": structure_type,
            "swing_points": swing_points[-8:],
            "bos": bos_list,
            "choch": choch_list,
            "last_swing_high": round(float(sh_prices[-1]), 5) if sh_prices else None,
            "last_swing_low":  round(float(sl_prices[-1]), 5) if sl_prices else None,
        }
