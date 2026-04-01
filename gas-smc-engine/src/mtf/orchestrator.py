"""
SMC Orchestrator — Multi-Timeframe SMC Analysis
Runs all detectors on candle data and computes final confluence signal.
"""
from typing import List, Dict, Any

from src.detection.market_structure import MarketStructureDetector
from src.detection.zones            import ZonesDetector
from src.detection.liquidity        import LiquidityDetector
from src.detection.entry            import EntryTriggerDetector
from src.detection.time_context     import TimeContextFilter
from src.style.manager              import StyleManager


class Orchestrator:
    def __init__(self):
        self.market_structure = MarketStructureDetector()
        self.zones            = ZonesDetector()
        self.liquidity        = LiquidityDetector()
        self.entry            = EntryTriggerDetector()
        self.time_context     = TimeContextFilter()
        self.style_manager    = StyleManager()

    def analyze(self, request_data: dict) -> dict:
        """
        Main analysis entry point.
        request_data must contain:
          - symbol   (str)
          - timeframe (str)
          - candles  (list of OHLCV dicts: time, open, high, low, close, volume)
          - options  (dict with trading_style)
        """
        symbol        = request_data.get("symbol", "UNKNOWN")
        timeframe     = request_data.get("timeframe", "H1")
        candles_raw   = request_data.get("candles", [])
        options       = request_data.get("options", {})
        trading_style = options.get("trading_style", "intraday") if isinstance(options, dict) else getattr(options, "trading_style", "intraday")

        # Normalise candles: handle both Pydantic models and plain dicts
        candles: List[Dict] = []
        for c in candles_raw:
            if hasattr(c, "dict"):
                candles.append(c.dict())
            elif isinstance(c, dict):
                candles.append(c)

        # ── Run all detectors ──────────────────────────────────────────────────
        ms_result   = self.market_structure.detect(candles)
        zone_result = self.zones.detect(candles)
        liq_result  = self.liquidity.detect(candles)
        tc_result   = self.time_context.detect(candles)

        # Pass market bias to entry detector for better confluence
        market_bias = ms_result.get("bias", "NEUTRAL")
        entry_result = self.entry.detect(candles, options, market_bias)

        # ── Confluence Score ───────────────────────────────────────────────────
        score, final_action = self._compute_confluence(
            ms_result, zone_result, liq_result, entry_result, tc_result, market_bias
        )

        # ── Final Signal ───────────────────────────────────────────────────────
        current_price = entry_result.get("current_price", 0)
        entry_rec     = entry_result.get("recommended_entry", {})
        ote           = entry_result.get("ote") or {}

        signal = {
            "action":        final_action,
            "confidence":    score,
            "entry_price":   entry_rec.get("entry", current_price),
            "stop_loss":     entry_rec.get("sl"),
            "take_profit":   entry_rec.get("tp"),
            "rr":            entry_rec.get("rr"),
            "market_bias":   market_bias,
            "in_kill_zone":  tc_result.get("in_kill_zone", False),
            "amd_phase":     tc_result.get("amd_phase", "UNKNOWN"),
            "reason":        entry_rec.get("reason", ""),
            "trade_quality": self._quality_label(score),
        }

        return {
            "symbol":           symbol,
            "timeframe":        timeframe,
            "trading_style":    trading_style,
            "candle_count":     len(candles),
            "market_structure": ms_result,
            "zones":            zone_result,
            "liquidity":        liq_result,
            "entry":            entry_result,
            "time_context":     tc_result,
            "signal":           signal,
            "confluence_score": score,
        }

    # ── Internal Confluence Calculator ─────────────────────────────────────────
    def _compute_confluence(
        self,
        ms: dict,
        zones: dict,
        liq: dict,
        entry: dict,
        tc: dict,
        bias: str,
    ) -> tuple:
        """
        Score 0–100 based on how many SMC conditions align.
        Returns (score, action).
        """
        score = 0

        # Market structure bias (25 pts)
        if bias in ("BULLISH", "BEARISH"):
            score += 20
        if ms.get("bos"):
            score += 5

        # CHoCH is uncertainty, slight reduction
        if ms.get("choch"):
            score -= 5

        # Zones alignment (20 pts)
        obs    = zones.get("order_blocks", [])
        fvgs   = zones.get("fvgs", [])
        sdzones = zones.get("supply_demand", [])

        entry_rec = entry.get("recommended_entry", {})
        entry_action = entry_rec.get("action", "WAIT")

        if obs:
            # Check if at least one OB aligns with bias
            for ob in obs:
                if bias == "BULLISH" and ob["type"] == "BULLISH_OB":
                    score += 10
                    break
                elif bias == "BEARISH" and ob["type"] == "BEARISH_OB":
                    score += 10
                    break

        if fvgs:
            score += 5

        if sdzones:
            score += 5

        # Liquidity context (15 pts)
        sweeps = liq.get("sweeps", [])
        if sweeps:
            last_sweep = sweeps[-1]
            if bias == "BULLISH" and last_sweep.get("type") == "BULLISH_SWEEP":
                score += 15   # stop hunt below before bullish move
            elif bias == "BEARISH" and last_sweep.get("type") == "BEARISH_SWEEP":
                score += 15   # stop hunt above before bearish move
            else:
                score += 5    # sweep exists but not aligned

        # Entry trigger (25 pts)
        ote = entry.get("ote") or {}
        if ote.get("in_ote_zone"):
            score += 15

        pattern = entry.get("candle_pattern", {})
        pat_bias = pattern.get("bias", "NEUTRAL")
        if pat_bias == bias:
            score += 10
        elif pat_bias != "NEUTRAL":
            score -= 5

        # Time context (15 pts)
        if tc.get("in_kill_zone"):
            score += 10
        if tc.get("is_high_prob_window"):
            score += 5
        if tc.get("amd_phase") == "MANIPULATION":
            score -= 5    # manipulation phase = higher uncertainty

        # Clamp to 0–100
        score = max(0, min(100, score))

        # Determine action
        if score >= 65 and bias == "BULLISH" and entry_action in ("BUY", "WAIT"):
            action = "BUY"
        elif score >= 65 and bias == "BEARISH" and entry_action in ("SELL", "WAIT"):
            action = "SELL"
        elif score >= 50:
            action = "WATCH"   # conditions building, not fully confluent
        else:
            action = "WAIT"

        return score, action

    @staticmethod
    def _quality_label(score: int) -> str:
        if score >= 80:
            return "A+"
        elif score >= 70:
            return "A"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C"
        else:
            return "SKIP"
