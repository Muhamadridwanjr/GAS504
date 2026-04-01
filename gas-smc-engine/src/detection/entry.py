"""
Entry Trigger Detector — Real SMC Implementation
Detects: OTE (Optimal Trade Entry 0.618–0.786 Fib), Candle Patterns (Pin Bar, Engulfing, Doji, Marubozu)
"""
import pandas as pd
from typing import List, Dict, Any, Optional


class EntryTriggerDetector:
    def detect(self, candles: List[Dict], params: dict = None, market_bias: str = "NEUTRAL") -> Dict[str, Any]:
        if not candles or len(candles) < 10:
            return {
                "ote": None,
                "candle_pattern": {"pattern": "NONE", "bias": "NEUTRAL"},
                "recommended_entry": {"action": "WAIT", "reason": "Insufficient data"},
            }

        df = pd.DataFrame(candles)
        df = df.sort_values("time").reset_index(drop=True)
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)

        current_price = float(df["close"].iloc[-1])
        ote     = self._calculate_ote(df, current_price)
        pattern = self._detect_candle_pattern(df)

        return {
            "ote":               ote,
            "candle_pattern":    pattern,
            "current_price":     round(current_price, 5),
            "recommended_entry": self._get_recommended_entry(ote, pattern, current_price, market_bias),
        }

    # ── OTE (Fibonacci 61.8%–78.6% Retracement) ───────────────────────────────
    def _calculate_ote(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Find the most recent significant impulse leg (last 30 bars).
        OTE zone = retracement into 61.8%–78.6% of that leg.
        Bullish leg: swing low → swing high → retrace down into 61.8–78.6%.
        Bearish leg: swing high → swing low → retrace up into 61.8–78.6%.
        """
        recent = df.tail(40)

        swing_high = float(recent["high"].max())
        swing_low  = float(recent["low"].min())
        hi_idx     = int(recent["high"].idxmax())
        lo_idx     = int(recent["low"].idxmin())
        leg_size   = swing_high - swing_low

        if leg_size == 0:
            return None

        # High came AFTER low → bullish leg; OTE = pullback into 61.8–78.6%
        if hi_idx > lo_idx:
            fib_618  = swing_high - leg_size * 0.618
            fib_786  = swing_high - leg_size * 0.786
            ote_top  = max(fib_618, fib_786)
            ote_bot  = min(fib_618, fib_786)
            ote_type = "BULLISH_OTE"
            desc     = "OTE Bullish — buy zone between 61.8–78.6% pullback"
        # Low came AFTER high → bearish leg; OTE = retrace up into 61.8–78.6%
        else:
            fib_618  = swing_low + leg_size * 0.618
            fib_786  = swing_low + leg_size * 0.786
            ote_top  = max(fib_618, fib_786)
            ote_bot  = min(fib_618, fib_786)
            ote_type = "BEARISH_OTE"
            desc     = "OTE Bearish — sell zone between 61.8–78.6% retrace"

        in_zone = ote_bot <= current_price <= ote_top

        return {
            "type":        ote_type,
            "fib_618":     round(fib_618, 5),
            "fib_786":     round(fib_786, 5),
            "ote_top":     round(ote_top, 5),
            "ote_bottom":  round(ote_bot, 5),
            "swing_high":  round(swing_high, 5),
            "swing_low":   round(swing_low, 5),
            "in_ote_zone": in_zone,
            "description": desc,
        }

    # ── Candle Pattern Detection ───────────────────────────────────────────────
    def _detect_candle_pattern(self, df: pd.DataFrame) -> Dict:
        """Detect reversal and continuation candle patterns on the last 3 candles."""
        if len(df) < 3:
            return {"pattern": "NONE", "bias": "NEUTRAL"}

        c  = df.iloc[-1]   # current candle
        p  = df.iloc[-2]   # previous candle
        pp = df.iloc[-3]   # candle before previous

        c_open, c_high, c_low, c_close = float(c["open"]), float(c["high"]), float(c["low"]), float(c["close"])
        p_open, p_high, p_low, p_close = float(p["open"]), float(p["high"]), float(p["low"]), float(p["close"])

        body        = abs(c_close - c_open)
        upper_wick  = c_high - max(c_close, c_open)
        lower_wick  = min(c_close, c_open) - c_low
        total_range = c_high - c_low

        if total_range == 0:
            return {"pattern": "DOJI", "bias": "NEUTRAL", "description": "Doji — complete indecision"}

        # Doji: body < 10% of range
        if body < total_range * 0.10:
            return {"pattern": "DOJI", "bias": "NEUTRAL", "description": "Doji — indecision candle, wait for next candle confirmation"}

        # Hammer / Bullish Pin Bar: long lower wick ≥ 2× body, tiny upper wick
        if lower_wick >= body * 2.0 and upper_wick <= body * 0.5:
            return {
                "pattern":     "HAMMER",
                "bias":        "BULLISH",
                "description": "Bullish Pin Bar / Hammer — strong rejection of lower prices (buy signal)",
            }

        # Shooting Star / Bearish Pin Bar: long upper wick ≥ 2× body, tiny lower wick
        if upper_wick >= body * 2.0 and lower_wick <= body * 0.5:
            return {
                "pattern":     "SHOOTING_STAR",
                "bias":        "BEARISH",
                "description": "Bearish Pin Bar / Shooting Star — strong rejection of higher prices (sell signal)",
            }

        # Bullish Engulfing
        if (c_close > c_open and            # current bullish
                p_close < p_open and        # previous bearish
                c_close > p_open and        # current close > prev open
                c_open  < p_close):         # current open < prev close
            return {
                "pattern":     "BULLISH_ENGULFING",
                "bias":        "BULLISH",
                "description": "Bullish Engulfing — strong reversal signal, buyers overwhelmed sellers",
            }

        # Bearish Engulfing
        if (c_close < c_open and            # current bearish
                p_close > p_open and        # previous bullish
                c_close < p_open and        # current close < prev open
                c_open  > p_close):         # current open > prev close
            return {
                "pattern":     "BEARISH_ENGULFING",
                "bias":        "BEARISH",
                "description": "Bearish Engulfing — strong reversal signal, sellers overwhelmed buyers",
            }

        # Bullish Marubozu: strong full-body bullish (almost no wicks)
        if (c_close > c_open and
                upper_wick <= body * 0.1 and
                lower_wick <= body * 0.1):
            return {
                "pattern":     "BULLISH_MARUBOZU",
                "bias":        "BULLISH",
                "description": "Bullish Marubozu — full buying momentum, continuation likely",
            }

        # Bearish Marubozu
        if (c_close < c_open and
                upper_wick <= body * 0.1 and
                lower_wick <= body * 0.1):
            return {
                "pattern":     "BEARISH_MARUBOZU",
                "bias":        "BEARISH",
                "description": "Bearish Marubozu — full selling momentum, continuation likely",
            }

        # Bullish Inside Bar (potential breakout setup)
        if c_high < p_high and c_low > p_low:
            bias = "BULLISH" if c_close > c_open else "BEARISH"
            return {
                "pattern":     "INSIDE_BAR",
                "bias":        bias,
                "description": f"Inside Bar — compression before breakout, direction TBD",
            }

        return {"pattern": "NONE", "bias": "NEUTRAL", "description": "No significant pattern on last candle"}

    # ── Recommended Entry (OTE + Pattern confluence) ──────────────────────────
    def _get_recommended_entry(
        self,
        ote: Optional[Dict],
        pattern: Dict,
        current_price: float,
        market_bias: str,
    ) -> Dict:
        """
        HIGH confluence: in OTE zone + pattern confirms direction + market bias aligns.
        MEDIUM: in OTE zone OR pattern confirms alone.
        LOW / WAIT: no alignment.
        """
        if not ote:
            return {"action": "WAIT", "confidence": "LOW", "reason": "OTE could not be calculated"}

        in_ote       = ote.get("in_ote_zone", False)
        pat_bias     = pattern.get("bias", "NEUTRAL")
        ote_type     = ote.get("type", "")
        pat_name     = pattern.get("pattern", "NONE")
        swing_high   = ote.get("swing_high", current_price * 1.01)
        swing_low    = ote.get("swing_low",  current_price * 0.99)

        is_bullish_aligned = (
            in_ote and pat_bias == "BULLISH" and "BULLISH" in ote_type and
            (market_bias in ("BULLISH", "NEUTRAL"))
        )
        is_bearish_aligned = (
            in_ote and pat_bias == "BEARISH" and "BEARISH" in ote_type and
            (market_bias in ("BEARISH", "NEUTRAL"))
        )

        if is_bullish_aligned:
            sl = round(swing_low * 0.9995, 5)
            tp = round(swing_high, 5)
            rr = round((tp - current_price) / max(current_price - sl, 1e-9), 2)
            return {
                "action":      "BUY",
                "confidence":  "HIGH",
                "entry":       round(current_price, 5),
                "sl":          sl,
                "tp":          tp,
                "rr":          f"1:{rr}",
                "reason":      f"Price in OTE zone + {pat_name} confirms BUY. Market bias: {market_bias}.",
            }

        if is_bearish_aligned:
            sl = round(swing_high * 1.0005, 5)
            tp = round(swing_low, 5)
            rr = round((current_price - tp) / max(sl - current_price, 1e-9), 2)
            return {
                "action":      "SELL",
                "confidence":  "HIGH",
                "entry":       round(current_price, 5),
                "sl":          sl,
                "tp":          tp,
                "rr":          f"1:{rr}",
                "reason":      f"Price in OTE zone + {pat_name} confirms SELL. Market bias: {market_bias}.",
            }

        if in_ote:
            return {
                "action":     "WAIT",
                "confidence": "MEDIUM",
                "reason":     f"Price in OTE zone but no candle pattern confirmation yet. Wait for {ote_type} trigger.",
            }

        return {
            "action":     "WAIT",
            "confidence": "LOW",
            "reason":     f"Price not in OTE zone ({ote.get('ote_bottom')}–{ote.get('ote_top')}). Wait for retracement.",
        }
