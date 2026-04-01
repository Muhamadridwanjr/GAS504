from typing import Dict, Tuple
from src.config import settings
from src.lib.logger import logger


class Scorer:
    def calculate_score(
        self,
        regime_data: Dict,
        pattern_data: Dict,
        statarb_data: Dict,
        trend_data: Dict = None,
        phase_data: Dict = None,
        orderflow_data: Dict = None,
    ) -> Tuple[float, float, str]:
        """
        Aggregate 6 engine results → (score, confidence, final_signal).
        Engines that return no data contribute 0 to score with no weight penalty.
        """
        trend_data     = trend_data     or {}
        phase_data     = phase_data     or {}
        orderflow_data = orderflow_data or {}

        total_score  = 0.0
        total_weight = 0.0
        total_conf   = 0.0

        regime = regime_data.get("regime", "RANGING")
        r_conf = regime_data.get("confidence", 0.5)

        # Dynamic weight adjustments based on regime
        w_pattern  = settings.weight_pattern
        w_statarb  = settings.weight_statarb
        w_trend    = settings.weight_trend
        w_phase    = settings.weight_phase
        w_orderflow = settings.weight_orderflow

        if regime == "TRENDING":
            w_pattern  *= 1.5
            w_statarb  *= 0.5
            w_trend    *= 1.5
        elif regime == "RANGING":
            w_pattern  *= 0.8
            w_statarb  *= 1.5
            w_trend    *= 0.7
        elif regime in ("BREAKOUT", "MOMENTUM"):
            w_orderflow *= 1.4
            w_trend     *= 1.2

        # ── Pattern ─────────────────────────────────────────────────────────────
        p_dir  = pattern_data.get("expected_direction", "NEUTRAL")
        p_conf = pattern_data.get("confidence", 0.0)
        if p_dir != "NEUTRAL" and p_conf > 0:
            p_val = 1.0 if p_dir == "BUY" else -1.0
            total_score  += (p_val * p_conf) * w_pattern
            total_weight += w_pattern
            total_conf   += p_conf * w_pattern

        # ── StatArb ──────────────────────────────────────────────────────────────
        s_dir  = statarb_data.get("signal", "NEUTRAL")
        s_conf = statarb_data.get("confidence", 0.0)
        if s_dir != "NEUTRAL" and s_conf > 0:
            s_val = 1.0 if s_dir in ("BUY", "LONG_SPREAD") else -1.0
            total_score  += (s_val * s_conf) * w_statarb
            total_weight += w_statarb
            total_conf   += s_conf * w_statarb

        # ── Trend ────────────────────────────────────────────────────────────────
        t_dir      = trend_data.get("direction", "NEUTRAL")
        t_strength = float(trend_data.get("strength", 0.0))
        if t_dir and t_dir != "NEUTRAL" and t_strength > 0:
            t_val = 1.0 if t_dir in ("UP", "BULLISH", "BUY") else -1.0
            total_score  += (t_val * t_strength) * w_trend
            total_weight += w_trend
            total_conf   += t_strength * w_trend

        # ── Market Phase ─────────────────────────────────────────────────────────
        ph_bias = phase_data.get("bias", phase_data.get("direction", "NEUTRAL"))
        ph_conf = float(phase_data.get("confidence", 0.0))
        if ph_bias and ph_bias != "NEUTRAL" and ph_conf > 0:
            ph_val = 1.0 if ph_bias in ("BULLISH", "UP", "BUY") else -1.0
            total_score  += (ph_val * ph_conf) * w_phase
            total_weight += w_phase
            total_conf   += ph_conf * w_phase

        # ── Orderflow ────────────────────────────────────────────────────────────
        of_pressure = orderflow_data.get("pressure", "NEUTRAL")
        of_strength = float(orderflow_data.get("strength", 0.0))
        if of_pressure and of_pressure != "NEUTRAL" and of_strength > 0:
            of_val = 1.0 if of_pressure in ("BUY", "BUYING", "BULL") else -1.0
            total_score  += (of_val * of_strength) * w_orderflow
            total_weight += w_orderflow
            total_conf   += of_strength * w_orderflow

        # ── Normalise ────────────────────────────────────────────────────────────
        if total_weight == 0:
            # No engines returned data — fall back to regime confidence only
            final_score = 0.0
            final_conf  = r_conf * 0.4
        else:
            final_score = total_score / total_weight
            final_conf  = total_conf  / total_weight

        signal = "NEUTRAL"
        if final_score >= settings.signal_threshold:
            signal = "BUY"
        elif final_score <= -settings.signal_threshold:
            signal = "SELL"

        logger.debug(
            f"Scorer: score={final_score:.3f} conf={final_conf:.3f} signal={signal} "
            f"regime={regime} engines_w={total_weight:.1f}"
        )
        return final_score, final_conf, signal


scorer = Scorer()
