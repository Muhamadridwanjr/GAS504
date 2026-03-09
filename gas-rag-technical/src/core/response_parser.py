"""
Response parser – converts raw LLM text output into structured AnalysisResult.
Handles JSON extraction from free-form or markdown-wrapped outputs.
"""
import json
import re
from typing import Any
from src.lib.logger import get_logger

logger = get_logger(__name__)


def parse_response(raw: str) -> dict[str, Any]:
    """
    Parse LLM raw output into a structured dict.
    Tries strict JSON parse first, falls back to regex extraction.
    """
    # 1. Try direct JSON parse
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    # 2. Extract JSON from markdown code fence
    pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(pattern, raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Find first { ... } block
    brace_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass

    # 4. Fallback: return partial data with raw reasoning
    logger.warning("Could not parse LLM response as JSON – using fallback")
    return _fallback_parse(raw)


def _fallback_parse(raw: str) -> dict[str, Any]:
    """Heuristic fallback when JSON extraction fails."""
    signal = "NEUTRAL"
    for word in ["BUY", "SELL", "BULLISH", "BEARISH"]:
        if word in raw.upper():
            signal = "BUY" if word in ("BUY", "BULLISH") else "SELL"
            break

    return {
        "summary": raw[:300].strip(),
        "key_levels": {"support": [], "resistance": []},
        "signal": signal,
        "confidence": 0.5,
        "entry": {"price": None, "stop_loss": None, "take_profit": []},
        "reasoning": raw,
        "short_term_bias": "sideways",
        "key_risks": [],
    }
