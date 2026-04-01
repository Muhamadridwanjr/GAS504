"""Multi-model consensus engine — weighted voting + agent specialization."""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from .prediction_engine import predict_single, _signal_strength

logger = logging.getLogger("consensus_engine")

MODELS = ["claude", "gpt", "gemini", "grok"]

# Agent specialization metadata
AGENT_SPEC = {
    "claude":  {"weight": 1.3, "specialty": "Accuracy & Reasoning",  "color": "#f59e0b"},
    "gpt":     {"weight": 1.2, "specialty": "General Market Context", "color": "#10b981"},
    "gemini":  {"weight": 1.0, "specialty": "Structure & Patterns",   "color": "#3b82f6"},
    "grok":    {"weight": 0.8, "specialty": "Fast Momentum",          "color": "#f43f5e"},
}

# Per-model perspective offsets (slight differentiation)
MODEL_OFFSETS = {
    "claude":  +2.0,
    "gpt":     +1.0,
    "gemini":  -0.5,
    "grok":    -1.5,
}
MODEL_CONF_OFFSETS = {
    "claude":  +3.5,
    "gpt":     +2.0,
    "gemini":  -1.0,
    "grok":    -2.5,
}


async def run_agent_predictions(
    question: str,
    category: str,
    yes_price: float,
    no_price: float,
    pair: Optional[str],
    selected_models: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Run all model predictions concurrently with specialization."""
    models_to_run = selected_models or MODELS

    async def run_one(model: str) -> Dict[str, Any]:
        result = await predict_single(question, category, yes_price, no_price, pair, model)
        spec = AGENT_SPEC.get(model, {"weight": 1.0, "specialty": "General", "color": "#6366f1"})

        if result.get("skipped"):
            return {
                "model": model,
                "yes": 50.0,
                "no": 50.0,
                "confidence": 40.0,
                "action": "NO TRADE",
                "signal_strength": "NO TRADE",
                "reasoning": result["reasoning"],
                "weight": spec["weight"],
                "specialty": spec["specialty"],
                "color": spec["color"],
            }

        offset = MODEL_OFFSETS.get(model, 0)
        conf_offset = MODEL_CONF_OFFSETS.get(model, 0)
        yes = round(max(5.0, min(95.0, result["yes"] + offset)), 1)
        no = round(100.0 - yes, 1)
        conf = round(max(40.0, min(98.0, result["confidence"] + conf_offset)), 1)

        return {
            "model": model,
            "yes": yes,
            "no": no,
            "confidence": conf,
            "action": result["action"],
            "signal_strength": _signal_strength(yes),
            "reasoning": result["reasoning"],
            "weight": spec["weight"],
            "specialty": spec["specialty"],
            "color": spec["color"],
        }

    results = await asyncio.gather(*[run_one(m) for m in models_to_run], return_exceptions=True)
    return [r for r in results if isinstance(r, dict)]


def build_consensus(agents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Weighted voting consensus with signal strength."""
    if not agents:
        return {
            "yes": 50.0, "no": 50.0, "action": "NO TRADE",
            "signal_strength": "NO TRADE", "confidence": 40.0,
            "majority_yes": 0, "majority_no": 0, "total_weight": 0.0,
        }

    total_weight = sum(a.get("weight", 1.0) for a in agents)

    # Weighted average YES
    weighted_yes = sum(a["yes"] * a.get("weight", 1.0) for a in agents) / total_weight
    weighted_conf = sum(a["confidence"] * a.get("weight", 1.0) for a in agents) / total_weight

    weighted_yes = round(weighted_yes, 1)
    weighted_conf = round(weighted_conf, 1)

    # Weighted votes
    votes_yes_w = sum(a.get("weight", 1.0) for a in agents if a["yes"] >= 58)
    votes_no_w  = sum(a.get("weight", 1.0) for a in agents if a["yes"] <= 42)
    votes_yes   = sum(1 for a in agents if a["yes"] >= 58)
    votes_no    = sum(1 for a in agents if a["yes"] <= 42)

    # Consensus: weighted majority + directional threshold
    if votes_yes_w >= total_weight * 0.55 and weighted_yes >= 60:
        if weighted_yes >= 75:
            action = "STRONG BUY YES"
        elif weighted_yes >= 65:
            action = "BUY YES"
        else:
            action = "WEAK YES"
    elif votes_no_w >= total_weight * 0.55 and weighted_yes <= 40:
        if weighted_yes <= 25:
            action = "STRONG BUY NO"
        elif weighted_yes <= 35:
            action = "BUY NO"
        else:
            action = "WEAK NO"
    else:
        action = "NO TRADE"

    return {
        "yes": weighted_yes,
        "no": round(100.0 - weighted_yes, 1),
        "action": action,
        "signal_strength": action,
        "confidence": weighted_conf,
        "majority_yes": votes_yes,
        "majority_no": votes_no,
        "total_weight": round(total_weight, 2),
    }
