import asyncio
import uuid
from typing import Dict, Any, List, Optional
from src.core.engine_clients import engine_clients
from src.core.scorer import scorer
from src.lib.logger import logger

class Orchestrator:
    async def analyze(self, symbol: str, timeframe: str = "H1", engines: List[str] = None) -> Dict[str, Any]:
        """
        Orchestrate parallel calls to edge quant engines and aggregate their signals.
        """
        if not engines:
            engines = ["regime", "pattern", "statarb"]
            
        logger.info(f"Orchestrating analysis for {symbol} ({timeframe}) across engines: {engines}")
        
        # We can fire them off concurrently
        tasks = []
        
        # Features might be needed by some engines, though usually they fetch their own
        if "regime" in engines:
            # We assume regime endpoint is GET /regime?symbol=X&timeframe=Y
            tasks.append(engine_clients.fetch_regime(symbol, timeframe))
        else:
            tasks.append(self._dummy_result({"regime": "UNKNOWN"}))
            
        if "pattern" in engines:
            tasks.append(engine_clients.fetch_pattern(symbol, timeframe))
        else:
             tasks.append(self._dummy_result({"expected_direction": "NEUTRAL"}))
             
        if "statarb" in engines:
            # StatArb usually takes pairs like XAUUSD_DXY. We will try a default if single symbol passed.
            # In a real system, we'd map single symbol to relevant pairs. For now:
            pair_name = f"{symbol}_DXY" if symbol != "DXY" else "EURUSD_GBPUSD"
            tasks.append(engine_clients.fetch_statarb(pair_name))
        else:
            tasks.append(self._dummy_result({"signal": "NEUTRAL"}))
            
        # Await all concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        regime_res = results[0] if not isinstance(results[0], Exception) and results[0] else {}
        pattern_res = results[1] if not isinstance(results[1], Exception) and results[1] else {}
        statarb_res = results[2] if not isinstance(results[2], Exception) and results[2] else {}

        # Scoring
        score, conf, final_sig = scorer.calculate_score(regime_res, pattern_res, statarb_res)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": final_sig,
            "confidence": round(conf, 4),
            "score": round(score, 4),
            "details": {
                "regime": regime_res,
                "pattern": pattern_res,
                "statarb": statarb_res
            }
        }

    async def _dummy_result(self, default_val: Dict = None) -> Dict:
        return default_val or {}

    async def generate_gas_signal(
        self,
        symbol: str,
        timeframe: str = "M15",
        market: Optional[Dict] = None,
        session: str = "OFF",
        context: Optional[Dict] = None,
        engines: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate full GAS AI signal as expected by GASSTRATEGYEAPRO v4.0.
        Returns all fields: signal_id, action, entry, sl, tp1, tp_final, lot,
        reason, observation, trading_plan, risk_management, journal, backtest,
        psychology, mindset, regime, session, confidence.
        """
        if not engines:
            engines = ["regime", "pattern", "statarb"]

        market = market or {}
        context = context or {}

        bid = market.get("bid", 0)
        ask = market.get("ask", 0)
        spread = market.get("spread", 0)
        atr = market.get("atr_14_m15", 0)
        mid_price = (bid + ask) / 2 if bid and ask else 0

        fixed_lot = context.get("fixed_lot", 0.01)
        max_spread = context.get("max_spread", 5000)
        consecutive_loss = context.get("consecutive_loss", 0)

        # Spread guard
        if max_spread > 0 and spread > max_spread:
            return self._gas_none_signal(symbol, session, "Spread too high")

        # Run engine analysis
        analysis = await self.analyze(symbol, timeframe, engines)
        final_signal = analysis.get("signal", "NEUTRAL")
        confidence = analysis.get("confidence", 0.5)
        score = analysis.get("score", 0)
        regime_data = analysis.get("details", {}).get("regime", {})
        regime = regime_data.get("regime", "UNKNOWN")
        regime_conf = regime_data.get("confidence", 0.0)

        # If engines lack real data but regime is confident, use regime-based signal
        if (final_signal == "NEUTRAL" or confidence < 0.35) and regime_conf >= 0.7 and session != "OFF":
            final_signal, confidence = self._regime_signal(regime, regime_conf, context)
            logger.info(f"Regime-based signal fallback | {final_signal} | regime={regime} | conf={confidence:.2f}")

        # If still no clear direction, return WAIT
        if final_signal == "NEUTRAL" or confidence < 0.35:
            return self._gas_none_signal(symbol, session, f"No confluence (conf={confidence:.2f})")

        # Only trade during kill zones for lower-confidence signals
        if session == "OFF" and confidence < 0.80:
            return self._gas_none_signal(symbol, session, "Outside kill zone, confidence too low")

        # Compute levels from ATR
        if atr <= 0:
            # Fallback ATR estimate (0.1% of price)
            atr = mid_price * 0.001 if mid_price > 0 else 5.0

        action = final_signal  # BUY or SELL
        digits = self._get_digits(symbol)

        if action == "BUY":
            entry = round(ask, digits) if ask else round(mid_price, digits)
            sl = round(entry - atr * 2.0, digits)
            tp1 = round(entry + atr * 3.0, digits)
            tp_final = round(entry + atr * 5.5, digits)
        else:  # SELL
            entry = round(bid, digits) if bid else round(mid_price, digits)
            sl = round(entry + atr * 2.0, digits)
            tp1 = round(entry - atr * 3.0, digits)
            tp_final = round(entry - atr * 5.5, digits)

        # Validate levels
        if entry <= 0 or sl <= 0:
            return self._gas_none_signal(symbol, session, "Invalid price levels")

        grade = self._grade_signal(confidence, consecutive_loss, session)
        level = self._level_signal(confidence)
        reason = self._build_reason(action, regime, session, analysis, grade)

        signal_id = str(uuid.uuid4())
        logger.info(f"GAS signal generated | {action} {symbol} | conf={confidence:.2f} | grade={grade} | session={session}")

        return {
            "signal_id": signal_id,
            "action": action,
            "symbol": symbol,
            "entry": entry,
            "sl": sl,
            "tp1": tp1,
            "tp_final": tp_final,
            "lot": fixed_lot,
            "reason": reason,
            "observation": (
                f"Price at {entry:.{digits}f} | ATR={atr:.{digits}f} | "
                f"Spread={spread}pts | Regime={regime} | Score={score:.3f}"
            ),
            "trading_plan": (
                f"{'Enter BUY at ask' if action=='BUY' else 'Enter SELL at bid'}, "
                f"SL={sl:.{digits}f}, TP1={tp1:.{digits}f}, TP_Final={tp_final:.{digits}f}. "
                f"Move BE after +300pts. Partial close 50% at TP1."
            ),
            "risk_management": (
                f"Fixed lot {fixed_lot} | SL={atr*2:.{digits}f} pts from entry | "
                f"RR=1:{round(atr*5.5/atr*2, 1) if atr > 0 else 2.5:.1f} | "
                f"Max spread={max_spread}pts"
            ),
            "journal": (
                f"Session={session} | Grade={grade} | Level={level} | "
                f"Consecutive losses={consecutive_loss} | "
                f"Confidence={confidence*100:.1f}%"
            ),
            "backtest": (
                f"ICT+SMC {action} setup | Regime={regime} | "
                f"Session={session} kill zone confluence"
            ),
            "psychology": (
                "Patient execution only. A+ setups. No FOMO. "
                "If in doubt, stay out." if confidence < 0.7 else
                "High confidence setup. Execute per plan. Trust the system."
            ),
            "mindset": "Process > Profit. Protect capital first. Trust the system.",
            "regime": regime,
            "session": session,
            "confidence": round(confidence, 4),
            "grade": grade,
            "level": level,
            "timeframe": timeframe,
        }

    def _regime_signal(self, regime: str, regime_conf: float, context: Dict) -> tuple:
        """
        Rule-based signal when ML engines lack sufficient data.
        Uses regime + session to determine direction and confidence.
        """
        consecutive_loss = context.get("consecutive_loss", 0)
        penalty = consecutive_loss * 0.05

        if regime == "TRENDING":
            # In trending regime, follow the trend – use a conservative SELL (bearish bias default)
            # In a real system, we'd determine trend direction from price action
            return "SELL", max(0.55, regime_conf * 0.7 - penalty)
        elif regime == "RANGING":
            # In ranging, mean reversion is possible from either side
            # Slight SELL bias in NY session (risk-off tendency)
            return "SELL", max(0.50, regime_conf * 0.65 - penalty)
        elif regime in ("BREAKOUT", "MOMENTUM"):
            return "BUY", max(0.55, regime_conf * 0.70 - penalty)
        return "NEUTRAL", 0.0

    def _gas_none_signal(self, symbol: str, session: str, reason: str) -> Dict:
        return {
            "signal_id": "",
            "action": "NONE",
            "symbol": symbol,
            "entry": 0, "sl": 0, "tp1": 0, "tp_final": 0, "lot": 0,
            "reason": reason,
            "observation": "", "trading_plan": "", "risk_management": "",
            "journal": f"Session={session}", "backtest": "",
            "psychology": "Wait for valid setup. No FOMO.",
            "mindset": "Process > Profit. Trust the system.",
            "regime": "UNKNOWN", "session": session, "confidence": 0,
        }

    def _get_digits(self, symbol: str) -> int:
        symbol = symbol.upper()
        if any(x in symbol for x in ["JPY", "XAG"]):
            return 3
        if any(x in symbol for x in ["XAU", "BTC", "ETH", "US30", "US500", "NAS"]):
            return 2
        return 5

    def _grade_signal(self, confidence: float, consecutive_loss: int, session: str) -> str:
        if consecutive_loss >= 2:
            return "C"
        if confidence >= 0.85 and session != "OFF":
            return "A+"
        if confidence >= 0.75:
            return "A"
        if confidence >= 0.60:
            return "B+"
        return "B"

    def _level_signal(self, confidence: float) -> str:
        if confidence >= 0.80:
            return "HOT"
        if confidence >= 0.65:
            return "VALID"
        return "WAIT SETUP"

    def _build_reason(
        self,
        action: str,
        regime: str,
        session: str,
        analysis: Dict,
        grade: str,
    ) -> str:
        pattern = analysis.get("details", {}).get("pattern", {})
        statarb = analysis.get("details", {}).get("statarb", {})
        parts = [f"{action} signal | Regime={regime} | Session={session} | Grade={grade}"]
        p_dir = pattern.get("expected_direction", "")
        if p_dir:
            parts.append(f"Pattern={p_dir}")
        s_sig = statarb.get("signal", "")
        if s_sig:
            parts.append(f"StatArb={s_sig}")
        return " | ".join(parts)


orchestrator = Orchestrator()
