"""
Liquidity Detector — Real SMC Implementation
Detects: Liquidity Pools (Equal Highs/Lows), Sweeps (Stop Hunts), Inducements
"""
import pandas as pd
from typing import List, Dict, Any


class LiquidityDetector:
    def detect(self, candles: List[Dict], params: dict = None) -> Dict[str, Any]:
        if not candles or len(candles) < 15:
            return {"pools": [], "sweeps": [], "inducements": []}

        df = pd.DataFrame(candles)
        df = df.sort_values("time").reset_index(drop=True)
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)

        current_price = float(df["close"].iloc[-1])

        return {
            "pools":       self._detect_pools(df, current_price),
            "sweeps":      self._detect_sweeps(df),
            "inducements": self._detect_inducements(df, current_price),
        }

    # ── Liquidity Pools (Equal Highs / Equal Lows) ─────────────────────────────
    def _detect_pools(self, df: pd.DataFrame, current_price: float) -> List[Dict]:
        """
        Equal highs within tolerance = buy-side liquidity pool (cluster of buy stops).
        Equal lows  within tolerance = sell-side liquidity pool (cluster of sell stops).
        Tolerance: 0.1% of price — tight enough for crypto & forex.
        """
        pools = []
        n = len(df)
        tolerance = 0.0015  # 0.15%

        highs = df["high"].values.tolist()
        lows  = df["low"].values.tolist()
        times = df["time"].values.tolist()

        seen_levels: set = set()

        # Look at last 30 bars for equal levels
        start = max(0, n - 30)

        for i in range(start, n):
            for j in range(start, i):
                # Equal highs → buy-side liquidity
                if highs[j] > 0 and abs(highs[i] - highs[j]) / highs[j] < tolerance:
                    level = round((highs[i] + highs[j]) / 2, 5)
                    key = f"BSL_{level:.3f}"
                    if key not in seen_levels and current_price < level:
                        seen_levels.add(key)
                        pools.append({
                            "type":        "BUY_SIDE",
                            "level":       level,
                            "time_a":      int(times[j]),
                            "time_b":      int(times[i]),
                            "description": f"Buy-Side Liquidity Pool @ {level} — cluster of stop losses above (likely target)",
                        })

                # Equal lows → sell-side liquidity
                if lows[j] > 0 and abs(lows[i] - lows[j]) / lows[j] < tolerance:
                    level = round((lows[i] + lows[j]) / 2, 5)
                    key = f"SSL_{level:.3f}"
                    if key not in seen_levels and current_price > level:
                        seen_levels.add(key)
                        pools.append({
                            "type":        "SELL_SIDE",
                            "level":       level,
                            "time_a":      int(times[j]),
                            "time_b":      int(times[i]),
                            "description": f"Sell-Side Liquidity Pool @ {level} — cluster of stop losses below (likely target)",
                        })

        # Sort by proximity to current price (closest first)
        pools.sort(key=lambda p: abs(p["level"] - current_price))
        return pools[:6]

    # ── Liquidity Sweeps (Stop Hunts) ──────────────────────────────────────────
    def _detect_sweeps(self, df: pd.DataFrame) -> List[Dict]:
        """
        Bullish sweep: candle wicked below previous N-bar low, then closed above it.
        Bearish sweep: candle wicked above previous N-bar high, then closed below it.
        These are stop hunts that signal smart money direction reversal.
        """
        sweeps = []
        n = len(df)
        lookback = 5

        for i in range(lookback, n):
            c_high  = float(df["high"].iloc[i])
            c_low   = float(df["low"].iloc[i])
            c_open  = float(df["open"].iloc[i])
            c_close = float(df["close"].iloc[i])
            t       = int(df["time"].iloc[i])

            prior_high = float(df["high"].iloc[i - lookback: i].max())
            prior_low  = float(df["low"].iloc[i - lookback: i].min())

            # Bullish sweep: wick below prior low, then closed above it (buy stop hunt)
            if (c_low < prior_low and
                    c_close > prior_low and
                    c_close > c_open):        # bullish close
                sweeps.append({
                    "type":         "BULLISH_SWEEP",
                    "swept_level":  round(prior_low, 5),
                    "candle_low":   round(c_low, 5),
                    "time":         t,
                    "description":  "Stop Hunt Below (Sell-Side Liquidity Swept) — Bullish reversal signal",
                })

            # Bearish sweep: wick above prior high, then closed below it (sell stop hunt)
            elif (c_high > prior_high and
                      c_close < prior_high and
                      c_close < c_open):      # bearish close
                sweeps.append({
                    "type":         "BEARISH_SWEEP",
                    "swept_level":  round(prior_high, 5),
                    "candle_high":  round(c_high, 5),
                    "time":         t,
                    "description":  "Stop Hunt Above (Buy-Side Liquidity Swept) — Bearish reversal signal",
                })

        return sweeps[-4:]

    # ── Inducements ────────────────────────────────────────────────────────────
    def _detect_inducements(self, df: pd.DataFrame, current_price: float) -> List[Dict]:
        """
        Minor swing high/low that appears as an obvious breakout target but is
        actually a trap used to grab liquidity before the real move.
        Identified as isolated swing extremes with smaller relative size.
        """
        inducements = []
        n = len(df)

        for i in range(2, n - 2):
            h = float(df["high"].iloc[i])
            l = float(df["low"].iloc[i])

            # Minor swing high (local peak)
            if (h > float(df["high"].iloc[i - 1]) and
                    h > float(df["high"].iloc[i + 1]) and
                    h > float(df["high"].iloc[i - 2]) and
                    h > float(df["high"].iloc[i + 2]) and
                    current_price < h):
                inducements.append({
                    "type":        "INDUCEMENT_HIGH",
                    "level":       round(h, 5),
                    "time":        int(df["time"].iloc[i]),
                    "description": f"Minor Swing High @ {h:.5f} — Inducement trap for breakout traders",
                })

            # Minor swing low (local trough)
            if (l < float(df["low"].iloc[i - 1]) and
                    l < float(df["low"].iloc[i + 1]) and
                    l < float(df["low"].iloc[i - 2]) and
                    l < float(df["low"].iloc[i + 2]) and
                    current_price > l):
                inducements.append({
                    "type":        "INDUCEMENT_LOW",
                    "level":       round(l, 5),
                    "time":        int(df["time"].iloc[i]),
                    "description": f"Minor Swing Low @ {l:.5f} — Inducement trap for breakdown traders",
                })

        # Return 3 most recent inducements
        return inducements[-3:]
