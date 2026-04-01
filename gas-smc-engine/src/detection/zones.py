"""
Zones Detector — Real SMC Implementation
Detects: Order Blocks (Bullish/Bearish), Fair Value Gaps (FVG), Supply/Demand Zones
"""
import pandas as pd
from typing import List, Dict, Any


class ZonesDetector:
    def detect(self, candles: List[Dict], params: dict = None) -> Dict[str, Any]:
        if not candles or len(candles) < 10:
            return {"order_blocks": [], "fvgs": [], "supply_demand": []}

        df = pd.DataFrame(candles)
        df = df.sort_values("time").reset_index(drop=True)
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)

        current_price = float(df["close"].iloc[-1])

        return {
            "order_blocks":  self._detect_order_blocks(df, current_price),
            "fvgs":          self._detect_fvg(df, current_price),
            "supply_demand": self._detect_supply_demand(df, current_price),
        }

    # ── Order Blocks ────────────────────────────────────────────────────────────
    def _detect_order_blocks(self, df: pd.DataFrame, current_price: float) -> List[Dict]:
        """
        Bullish OB : Last bearish candle BEFORE a strong bullish impulse (BOS up).
        Bearish OB : Last bullish candle BEFORE a strong bearish impulse (BOS down).
        An OB is invalidated (mitigated) when price closes through it.
        """
        obs = []
        n = len(df)
        avg_body = (df["close"] - df["open"]).abs().mean()
        if avg_body == 0:
            return []

        for i in range(1, n - 2):
            c_open  = float(df["open"].iloc[i])
            c_close = float(df["close"].iloc[i])
            c_high  = float(df["high"].iloc[i])
            c_low   = float(df["low"].iloc[i])
            n1_open  = float(df["open"].iloc[i + 1])
            n1_close = float(df["close"].iloc[i + 1])
            n1_body  = abs(n1_close - n1_open)

            # Bullish OB: bearish candle followed by impulsive bullish candle
            if (c_close < c_open and                          # current = bearish
                    n1_close > n1_open and                    # next    = bullish
                    n1_body > avg_body * 1.5):                # impulsive
                mitigated = current_price < c_low             # price wicked into OB
                if not mitigated and current_price > c_high:  # OB is below price
                    obs.append({
                        "type":        "BULLISH_OB",
                        "high":        round(c_high, 5),
                        "low":         round(c_low, 5),
                        "mid":         round((c_high + c_low) / 2, 5),
                        "time":        int(df["time"].iloc[i]),
                        "mitigated":   False,
                        "description": "Bullish Order Block — Institutional Demand Zone (buy on retest)",
                    })

            # Bearish OB: bullish candle followed by impulsive bearish candle
            elif (c_close > c_open and                        # current = bullish
                      n1_close < n1_open and                  # next    = bearish
                      n1_body > avg_body * 1.5):              # impulsive
                mitigated = current_price > c_high            # price wicked into OB
                if not mitigated and current_price < c_low:   # OB is above price
                    obs.append({
                        "type":        "BEARISH_OB",
                        "high":        round(c_high, 5),
                        "low":         round(c_low, 5),
                        "mid":         round((c_high + c_low) / 2, 5),
                        "time":        int(df["time"].iloc[i]),
                        "mitigated":   False,
                        "description": "Bearish Order Block — Institutional Supply Zone (sell on retest)",
                    })

        # Return 4 most recent unmitigated OBs
        return obs[-4:] if len(obs) > 4 else obs

    # ── Fair Value Gaps ─────────────────────────────────────────────────────────
    def _detect_fvg(self, df: pd.DataFrame, current_price: float) -> List[Dict]:
        """
        Bullish FVG : candle[i-1].high < candle[i+1].low  (gap above prior candle top)
        Bearish FVG : candle[i-1].low  > candle[i+1].high (gap below prior candle bottom)
        Imbalances are filled when price trades through the gap midpoint.
        """
        fvgs = []
        n = len(df)

        for i in range(1, n - 1):
            prev_high = float(df["high"].iloc[i - 1])
            prev_low  = float(df["low"].iloc[i - 1])
            next_high = float(df["high"].iloc[i + 1])
            next_low  = float(df["low"].iloc[i + 1])
            t         = int(df["time"].iloc[i])

            # Bullish FVG
            if prev_high < next_low:
                top    = next_low
                bottom = prev_high
                mid    = (top + bottom) / 2
                filled = current_price <= top and current_price >= bottom
                # Only surface FVGs close enough to current price (within 3% range)
                price_range = current_price * 0.03
                if abs(current_price - mid) < price_range or filled:
                    fvgs.append({
                        "type":        "BULLISH_FVG",
                        "top":         round(top, 5),
                        "bottom":      round(bottom, 5),
                        "mid":         round(mid, 5),
                        "gap_size":    round(top - bottom, 5),
                        "time":        t,
                        "filled":      filled,
                        "description": "Bullish FVG (Imbalance) — price tends to retrace to fill",
                    })

            # Bearish FVG
            elif prev_low > next_high:
                top    = prev_low
                bottom = next_high
                mid    = (top + bottom) / 2
                filled = current_price >= bottom and current_price <= top
                price_range = current_price * 0.03
                if abs(current_price - mid) < price_range or filled:
                    fvgs.append({
                        "type":        "BEARISH_FVG",
                        "top":         round(top, 5),
                        "bottom":      round(bottom, 5),
                        "mid":         round(mid, 5),
                        "gap_size":    round(top - bottom, 5),
                        "time":        t,
                        "filled":      filled,
                        "description": "Bearish FVG (Imbalance) — price tends to retrace to fill",
                    })

        return fvgs[-5:] if len(fvgs) > 5 else fvgs

    # ── Supply / Demand Zones ───────────────────────────────────────────────────
    def _detect_supply_demand(self, df: pd.DataFrame, current_price: float) -> List[Dict]:
        """
        Consolidation base (3-candle range) followed by impulsive breakout.
        Base range < 40% of impulse = valid S/D zone.
        """
        zones = []
        n = len(df)
        lookback = 3

        for i in range(lookback, n - 2):
            base_high = float(df["high"].iloc[i - lookback:i].max())
            base_low  = float(df["low"].iloc[i - lookback:i].min())
            base_range = base_high - base_low
            impulse   = abs(float(df["close"].iloc[i + 1]) - float(df["open"].iloc[i - lookback]))

            if base_range <= 0 or impulse < base_range * 2:
                continue

            # Bullish impulse → Demand zone below
            if float(df["close"].iloc[i + 1]) > float(df["open"].iloc[i - lookback]):
                if current_price > base_high:   # price is above zone = potential demand
                    zones.append({
                        "type":        "DEMAND",
                        "high":        round(base_high, 5),
                        "low":         round(base_low, 5),
                        "mid":         round((base_high + base_low) / 2, 5),
                        "time":        int(df["time"].iloc[i - lookback]),
                        "description": "Demand Zone — Expect buy orders on retest",
                    })
            # Bearish impulse → Supply zone above
            else:
                if current_price < base_low:    # price is below zone = potential supply
                    zones.append({
                        "type":        "SUPPLY",
                        "high":        round(base_high, 5),
                        "low":         round(base_low, 5),
                        "mid":         round((base_high + base_low) / 2, 5),
                        "time":        int(df["time"].iloc[i - lookback]),
                        "description": "Supply Zone — Expect sell orders on retest",
                    })

        return zones[-3:] if len(zones) > 3 else zones
