"""
GAS Strategy AI — AI Engine
Primary: Kimi 2.5 (Moonshot API) — signal & scanner
Fallback: DeepSeek via OpenRouter — general analysis
"""
import os
import json
from openai import AsyncOpenAI
from typing import Optional

# ── Kimi 2.5 (Moonshot AI) ───────────────────────────────────────────────────
KIMI_API_KEY = os.getenv("KIMI_API_KEY_ANALYSIS", "")
KIMI_BASE_URL = "https://api.moonshot.cn/v1"
KIMI_MODEL = "moonshot-v1-8k"

# ── OpenRouter ────────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")

# ── AI Model Tiers (plan-gated) ───────────────────────────────────────────────
# Plans: essential < plus < premium < ultimate
# Confirmed working on OpenRouter as of 2026-03-23.
MODEL_TIERS: dict = {
    # ── Essential plan ─────────────────────────────────────────────────────────
    "basic": {
        "model":        "deepseek/deepseek-chat",
        "label":        "GAS Basic",
        "description":  "DeepSeek V3 — cepat & efisien",
        "min_plan":     "essential",
        "signal_cost":  1,
        "scanner_cost": 5,
        "temperature":  0.3,
        "max_tokens":   1000,
        "badge":        "V3",
        "color":        "blue",
        "input_tokens": 2000,
        "output_tokens": 1000,
    },
    # ── Plus plan ──────────────────────────────────────────────────────────────
    "advanced": {
        "model":        "google/gemini-flash-1.5",
        "label":        "GAS Advanced",
        "description":  "Gemini Flash — cepat & akurat",
        "min_plan":     "plus",
        "signal_cost":  2,
        "scanner_cost": 8,
        "temperature":  0.25,
        "max_tokens":   1400,
        "badge":        "FLASH",
        "color":        "cyan",
        "input_tokens": 3000,
        "output_tokens": 2000,
    },
    # ── Premium plan ───────────────────────────────────────────────────────────
    "pro": {
        "model":        "anthropic/claude-haiku-4-5",
        "label":        "GAS Pro",
        "description":  "Claude Haiku — presisi institutional",
        "min_plan":     "premium",
        "signal_cost":  3,
        "scanner_cost": 12,
        "temperature":  0.2,
        "max_tokens":   1500,
        "badge":        "HAIKU",
        "color":        "emerald",
        "input_tokens": 4000,
        "output_tokens": 3000,
    },
    # ── Ultimate plan ──────────────────────────────────────────────────────────
    "ultra": {
        "model":        "anthropic/claude-sonnet-4-6",
        "label":        "GAS Ultra",
        "description":  "Claude Sonnet 4.6 — analisa premium",
        "min_plan":     "ultimate",
        "signal_cost":  5,
        "scanner_cost": 18,
        "temperature":  0.15,
        "max_tokens":   1800,
        "badge":        "SONNET",
        "color":        "amber",
        "input_tokens": 5000,
        "output_tokens": 4000,
    },
    "gpt": {
        "model":        "openai/gpt-4o",
        "label":        "GAS GPT",
        "description":  "GPT-4o — multi-perspektif OpenAI",
        "min_plan":     "ultimate",
        "signal_cost":  5,
        "scanner_cost": 18,
        "temperature":  0.2,
        "max_tokens":   1500,
        "badge":        "GPT",
        "color":        "teal",
        "input_tokens": 5000,
        "output_tokens": 4000,
    },
    # ── Ultra plan (new top tier) ───────────────────────────────────────────────
    "agent": {
        "model":        "anthropic/claude-opus-4-6",
        "label":        "GAS Agent",
        "description":  "Claude Opus 4.6 — AI Agent multi-model",
        "min_plan":     "ultra",
        "signal_cost":  10,
        "scanner_cost": 25,
        "temperature":  0.1,
        "max_tokens":   2000,
        "badge":        "AGENT",
        "color":        "rose",
        "input_tokens": 6000,
        "output_tokens": 5000,
    },
}

PLAN_ORDER = ["essential", "plus", "premium", "ultimate", "ultra"]

_kimi_client: Optional[AsyncOpenAI] = None
_or_client: Optional[AsyncOpenAI] = None


def get_kimi() -> AsyncOpenAI:
    global _kimi_client
    if _kimi_client is None:
        _kimi_client = AsyncOpenAI(api_key=KIMI_API_KEY, base_url=KIMI_BASE_URL)
    return _kimi_client


def get_client() -> AsyncOpenAI:
    global _or_client
    if _or_client is None:
        _or_client = AsyncOpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
    return _or_client


async def ask_kimi(system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
    """Call Kimi 2.5 (Moonshot API). Falls back to DeepSeek if key invalid."""
    if not KIMI_API_KEY or KIMI_API_KEY.startswith("sk-REPLACE"):
        return await ask_ai(system_prompt, user_prompt, max_tokens)
    try:
        client = get_kimi()
        response = await client.chat.completions.create(
            model=KIMI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        err = str(e)
        if "401" in err or "Authentication" in err or "Invalid" in err:
            # Key expired — fallback to DeepSeek via OpenRouter
            return await ask_ai(system_prompt, user_prompt, max_tokens)
        return f"[Kimi Error: {err}]"


async def ask_ai(system_prompt: str, user_prompt: str, max_tokens: int = 800) -> str:
    """Call DeepSeek via OpenRouter. No recursive fallback to avoid infinite loop."""
    try:
        client = get_client()
        response = await client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[AI Error: {str(e)[:80]}]"


def _parse_json(text: str) -> Optional[dict]:
    """Extract and parse first JSON object from AI response text.
    Handles: DeepSeek R1 <think> blocks, markdown code fences, raw JSON."""
    if not text or "[AI Error:" in text or "[Model Error:" in text or "[Kimi Error:" in text:
        return None
    try:
        clean = text

        # Strip DeepSeek R1 <think>...</think> reasoning block
        if "<think>" in clean:
            think_end = clean.find("</think>")
            if think_end >= 0:
                clean = clean[think_end + len("</think>"):]

        # Strip markdown code blocks
        if "```" in clean:
            # Find opening fence
            fence_start = clean.find("```")
            fence_end = clean.rfind("```")
            if fence_end > fence_start:
                inner = clean[fence_start:fence_end].lstrip("`json").lstrip("`").strip()
                # Check if inner has valid JSON
                s = inner.find("{")
                e = inner.rfind("}") + 1
                if s >= 0 and e > s:
                    try:
                        return json.loads(inner[s:e])
                    except Exception:
                        pass

        # Direct JSON extraction
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(clean[start:end])
    except Exception:
        pass
    return None


def _enforce_min_rr(entry: float, sl: float, tp1, tp2, tp3,
                     signal: str, pair: str = "") -> tuple:
    """Enforce minimum SL distance and RR 1:1.5 minimum. Fixes AI returning garbage TP values."""
    if not entry or not sl or entry == 0:
        return entry, sl, tp1, tp2, tp3

    is_buy = (signal == "BUY")
    diff = abs(float(entry) - float(sl))

    # Minimum SL distance per market type
    p = (pair or "").upper()
    if "XAU" in p or "GOLD" in p or "AG" in p:
        min_pct = 0.003   # XAUUSD: min 0.3% — at 3000 = 9 points
    elif "BTC" in p:
        min_pct = 0.010   # BTC: min 1%
    elif "ETH" in p:
        min_pct = 0.012   # ETH: min 1.2%
    elif any(x in p for x in ["USDT","USDC","SOL","BNB"]):
        min_pct = 0.008   # altcoin: min 0.8%
    elif "JPY" in p:
        min_pct = 0.0015  # JPY pairs: min 0.15%
    else:
        min_pct = 0.001   # forex: min 0.1% = 10 pips at 1.0

    min_diff = float(entry) * min_pct
    if diff < min_diff:
        diff = min_diff
        if is_buy:
            sl = round(float(entry) - diff, 5)
        else:
            sl = round(float(entry) + diff, 5)

    # Enforce TP minimum distances: TP1 >= 1.5×SL, TP2 >= 2.5×SL, TP3 >= 4×SL
    e = float(entry)
    if is_buy:
        min_tp1 = e + diff * 1.5
        min_tp2 = e + diff * 2.5
        min_tp3 = e + diff * 4.0
        tp1 = max(float(tp1), min_tp1) if tp1 else min_tp1
        tp2 = max(float(tp2), min_tp2) if tp2 else min_tp2
        tp3 = max(float(tp3), min_tp3) if tp3 else min_tp3
        # Sanity: TP1 must be above entry, TP2 above TP1, TP3 above TP2
        if tp1 <= e:  tp1 = min_tp1
        if tp2 <= tp1: tp2 = tp1 + diff
        if tp3 <= tp2: tp3 = tp2 + diff
    else:
        min_tp1 = e - diff * 1.5
        min_tp2 = e - diff * 2.5
        min_tp3 = e - diff * 4.0
        tp1 = min(float(tp1), min_tp1) if tp1 else min_tp1
        tp2 = min(float(tp2), min_tp2) if tp2 else min_tp2
        tp3 = min(float(tp3), min_tp3) if tp3 else min_tp3
        # Sanity: TP1 must be below entry, TP2 below TP1, TP3 below TP2
        if tp1 >= e:  tp1 = min_tp1
        if tp2 >= tp1: tp2 = tp1 - diff
        if tp3 >= tp2: tp3 = tp2 - diff

    prec = 5 if float(entry) < 10 else 2
    return round(e, prec), round(float(sl), prec), round(tp1, prec), round(tp2, prec), round(tp3, prec)


def _compute_sltp(indicators: dict, current_price: float, signal: str) -> tuple:
    """
    Compute entry/SL/TP from BB bands → SMC levels → EMA → fixed-pct.
    Called when AI is unavailable so the signal always has real SL/TP.
    Returns: (entry, sl, tp1, tp2, tp3, rr_str)
    """
    smc = indicators.get("SMC") or {}
    bb  = indicators.get("BB")  or {}
    ema = indicators.get("EMA") or {}

    # ── 1. Use SMC values if both entry and sl are present ────────────────────
    smc_entry = smc.get("smc_entry")
    smc_sl    = smc.get("smc_sl")
    smc_tp    = smc.get("smc_tp")
    if smc_entry and smc_sl and smc_entry != smc_sl:
        entry = float(smc_entry)
        sl    = float(smc_sl)
        diff  = abs(entry - sl)
        tp1   = float(smc_tp) if smc_tp else (entry + diff if signal == "BUY" else entry - diff)
        tp2   = entry + diff * 2 if signal == "BUY" else entry - diff * 2
        tp3   = entry + diff * 3 if signal == "BUY" else entry - diff * 3
        rr    = f"1:{abs(tp2 - entry) / diff:.1f}" if diff > 0 else "1:2"
        return round(entry, 5), round(sl, 5), round(tp1, 5), round(tp2, 5), round(tp3, 5), rr

    # ── 2. Use Bollinger Bands ────────────────────────────────────────────────
    bb_upper  = bb.get("upper")
    bb_middle = bb.get("middle")
    bb_lower  = bb.get("lower")
    if bb_upper and bb_lower and bb_middle:
        band = bb_upper - bb_lower
        margin = band * 0.08
        if signal == "SELL":
            entry = current_price
            sl    = round(bb_upper + margin, 5)
            tp1   = round(bb_middle, 5)
            tp2   = round(bb_lower, 5)
            tp3   = round(bb_lower - band * 0.25, 5)
        else:
            entry = current_price
            sl    = round(bb_lower - margin, 5)
            tp1   = round(bb_middle, 5)
            tp2   = round(bb_upper, 5)
            tp3   = round(bb_upper + band * 0.25, 5)
        diff = abs(entry - sl)
        rr   = f"1:{abs(tp2 - entry) / diff:.1f}" if diff > 0 else "1:2"
        return entry, sl, tp1, tp2, tp3, rr

    # ── 3. EMA-based ─────────────────────────────────────────────────────────
    e20 = ema.get("ema20")
    e50 = ema.get("ema50")
    if e20 and e50:
        atr_est = max(abs(current_price - e20), abs(e20 - e50)) * 0.8 or current_price * 0.003
        if signal == "SELL":
            sl  = round(current_price + atr_est * 1.5, 5)
            tp1 = round(current_price - atr_est, 5)
            tp2 = round(current_price - atr_est * 2, 5)
            tp3 = round(current_price - atr_est * 3, 5)
        else:
            sl  = round(current_price - atr_est * 1.5, 5)
            tp1 = round(current_price + atr_est, 5)
            tp2 = round(current_price + atr_est * 2, 5)
            tp3 = round(current_price + atr_est * 3, 5)
        return round(current_price, 5), sl, tp1, tp2, tp3, "1:2"

    # ── 4. Fixed percentage — market-aware (absolute last resort) ─────────────
    p = ""  # pair not available in this scope, use price-based heuristic
    if current_price > 1000:   pct = 0.004   # XAUUSD/BTC-like
    elif current_price > 100:  pct = 0.005
    elif current_price > 1:    pct = 0.008
    else:                      pct = 0.012
    if signal == "SELL":
        sl  = round(current_price * (1 + pct * 1.5), 5)
        tp1 = round(current_price * (1 - pct), 5)
        tp2 = round(current_price * (1 - pct * 2), 5)
        tp3 = round(current_price * (1 - pct * 3), 5)
    else:
        sl  = round(current_price * (1 - pct * 1.5), 5)
        tp1 = round(current_price * (1 + pct), 5)
        tp2 = round(current_price * (1 + pct * 2), 5)
        tp3 = round(current_price * (1 + pct * 3), 5)
    return round(current_price, 5), sl, tp1, tp2, tp3, "1:2"


def _build_technical_text(pair: str, timeframe: str, indicators: dict, current_price: float) -> str:
    """Build readable technical analysis text from indicator data — used when AI is unavailable."""
    rsi  = indicators.get("RSI", {}) or {}
    macd = indicators.get("MACD", {}) or {}
    ema  = indicators.get("EMA", {}) or {}
    adx  = indicators.get("ADX", {}) or {}
    bb   = indicators.get("BB", {}) or {}
    smc  = indicators.get("SMC", {}) or {}
    rec  = indicators.get("recommendation", "NEUTRAL")
    conf = indicators.get("confidence", 0)

    parts = [f"{pair} {timeframe} @ {current_price} — Analisis Teknikal:"]

    rsi_val = rsi.get("value")
    if rsi_val is not None:
        rsi_lbl = "OVERBOUGHT ⚠️" if rsi_val > 70 else "OVERSOLD ⚠️" if rsi_val < 30 else "NEUTRAL"
        parts.append(f"RSI(14) {rsi_val:.1f} ({rsi_lbl})")

    macd_sig = macd.get("signal", "")
    hist = macd.get("histogram")
    if macd_sig:
        parts.append(f"MACD {macd_sig} (hist {hist:.4f})" if hist is not None else f"MACD {macd_sig}")

    ema_sig = ema.get("signal", "")
    pve = ema.get("price_vs_ema20", "")
    if ema_sig:
        parts.append(f"EMA trend {ema_sig}, harga {pve} EMA20")

    bb_pos = bb.get("position", "")
    bb_sig = bb.get("signal", "")
    if bb_pos:
        parts.append(f"BB: price di zona {bb_pos} ({bb_sig})")

    adx_val = adx.get("value")
    if adx_val:
        parts.append(f"ADX {adx_val:.1f} — {adx.get('signal','')} ({adx.get('direction','')})")

    smc_bias = smc.get("bias", "")
    smc_phase = smc.get("amd_phase", "")
    smc_score = smc.get("smc_score", 0)
    if smc_bias:
        parts.append(f"SMC: Bias {smc_bias} | Phase {smc_phase} | Score {smc_score}/100")

    verdict = "Setup cukup kuat untuk dipertimbangkan." if conf >= 60 else "Tunggu konfirmasi tambahan sebelum entry."
    parts.append(f"→ Rekomendasi: {rec} ({conf}% confidence). {verdict}")

    return " | ".join(parts)


async def _ask_openrouter_model(model: str, system: str, user: str,
                                 temperature: float = 0.2, max_tokens: int = 1000) -> str:
    """Call any model via OpenRouter with given params."""
    try:
        client = get_client()
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Model Error ({model}): {str(e)[:100]}]"


# ── Plan depth mapping ────────────────────────────────────────────────────────
# Maps model_tier → analysis depth level (determines prompt complexity)
TIER_TO_PLAN_DEPTH: dict = {
    "basic":    "essential",   # DeepSeek V3   — indicator only
    "advanced": "plus",        # Gemini Flash  — smart confluence
    "pro":      "premium",     # Claude Haiku  — SMC + multi-TF
    "ultra":    "ultimate",    # Claude Sonnet — institutional + macro
    "gpt":      "ultimate",    # GPT-4o        — institutional + macro
    "agent":    "ultra",       # Claude Opus   — hedge fund mode
}

# ── Per-plan system identities (GAS Strategy AI official prompts) ─────────────
_SYSTEM_IDENTITY: dict = {
    # ── ESSENTIAL — Simple, fast, low cost ───────────────────────────────────
    "essential": (
        "Kamu adalah AI Trading Analyst - Golden AI Strategy (GAS).\n"
        "Mode: SIMPLE — cepat, efisien, fokus pada indikator dasar.\n\n"
        "GLOBAL RULES:\n"
        "- Gunakan data objektif, no asumsi liar\n"
        "- Jika tidak ada setup valid → output signal: NEUTRAL, order_type: WAIT\n"
        "- Prioritaskan risk management di atas segalanya\n"
        "- Hindari overtrading — hanya 1 setup terbaik\n"
        "- Output HARUS berupa JSON valid saja — TIDAK ada teks lain di luar JSON\n\n"
        "ANALYSIS STYLE: indikator doang (RSI, MACD, MA) — simple, singkat, tanpa narasi panjang.\n"
        " Untuk SL/TP: gunakan jarak yang realistis. XAUUSD minimum SL 8-15 points, TP1 minimum 1.5× SL distance. RR minimum 1:1.5. Jangan output SL/TP yang terlalu dekat dengan entry."
        "\n\nGRADE & STARS RUBRIC:\n"
        "- SS (stars 5): 88-100% confluence semua faktor align sempurna → MASUK SEKARANG\n"
        "- S  (stars 4-5): 78-88% confluence 4+ faktor align → HIGH CONFIDENCE\n"
        "- A+ (stars 4): 70-80% confluence 3-4 faktor align → VALID TRADE\n"
        "- A  (stars 3): 65-75% confluence 3 faktor → ACCEPTABLE, size kecil\n"
        "- B  (stars 2): 55-65% confluence lemah → TUNGGU konfirmasi lebih lanjut\n"
        "- C  (stars 1): <55% atau tidak ada setup valid → SKIP / NEUTRAL\n"
        "RULE: Jika signal BUY/SELL harus minimum grade B (stars 2). Jika tidak ada setup valid → NEUTRAL + grade C + stars 1.\n"
        "PROBABILITY GUIDANCE: SS=88-95, S=78-88, A+=72-80, A=65-75, B=55-65, C=30-55\n"
    ),

    # ── PLUS — Smart, multi-signal, confluence ────────────────────────────────
    "plus": (
        "Kamu adalah AI Trading Analyst - Golden AI Strategy (GAS).\n"
        "Mode: SMART — mulai ada confluence, multi-signal validation.\n\n"
        "GLOBAL RULES:\n"
        "- Gunakan data objektif, no asumsi liar\n"
        "- Jika tidak ada setup valid → output signal: NEUTRAL, order_type: WAIT\n"
        "- Prioritaskan risk management\n"
        "- Hindari overtrading\n"
        "- Output HARUS berupa JSON valid saja — TIDAK ada teks lain di luar JSON\n\n"
        "ANALYSIS STYLE: trend + RSI + MACD + MA → konfirmasi support/resistance → validasi entry "
        "→ cek session aktif (Asia/London/NY) → list minimal 3 faktor confluence.\n"
        " Untuk SL/TP: gunakan jarak yang realistis. XAUUSD minimum SL 8-15 points, TP1 minimum 1.5× SL distance. RR minimum 1:1.5. Jangan output SL/TP yang terlalu dekat dengan entry."
        "\n\nGRADE & STARS RUBRIC:\n"
        "- SS (stars 5): 88-100% confluence semua faktor align sempurna → MASUK SEKARANG\n"
        "- S  (stars 4-5): 78-88% confluence 4+ faktor align → HIGH CONFIDENCE\n"
        "- A+ (stars 4): 70-80% confluence 3-4 faktor align → VALID TRADE\n"
        "- A  (stars 3): 65-75% confluence 3 faktor → ACCEPTABLE, size kecil\n"
        "- B  (stars 2): 55-65% confluence lemah → TUNGGU konfirmasi lebih lanjut\n"
        "- C  (stars 1): <55% atau tidak ada setup valid → SKIP / NEUTRAL\n"
        "RULE: Jika signal BUY/SELL harus minimum grade B (stars 2). Jika tidak ada setup valid → NEUTRAL + grade C + stars 1.\n"
        "PROBABILITY GUIDANCE: SS=88-95, S=78-88, A+=72-80, A=65-75, B=55-65, C=30-55\n"
    ),

    # ── PREMIUM — SMC + structure + multi timeframe ───────────────────────────
    "premium": (
        "Kamu adalah AI Trading Analyst - Golden AI Strategy (GAS).\n"
        "Mode: PRO — SMC methodology + multi-timeframe structure analysis.\n\n"
        "GLOBAL RULES:\n"
        "- Gunakan data objektif, no asumsi liar\n"
        "- Jika tidak ada setup valid → output signal: NEUTRAL, order_type: WAIT\n"
        "- Prioritaskan risk management\n"
        "- Hindari overtrading\n"
        "- Output HARUS berupa JSON valid saja — TIDAK ada teks lain di luar JSON\n\n"
        "METHODOLOGY: ICT/SMC — Order Block (OB), Fair Value Gap (FVG), Liquidity Sweep, "
        "Break of Structure (BOS), Change of Character (CHoCH), OTE zone (61.8-78.6%), Kill Zone, AMD Phase.\n\n"
        "ANALYSIS STYLE:\n"
        "- Analisa 3 timeframe: H4 (HTF bias) → H1 (structure) → M15 (entry)\n"
        "- Deteksi BOS dan CHoCH untuk konfirmasi trend direction\n"
        "- Identifikasi Order Block dan FVG sebagai zona entry\n"
        "- Entry harus dari pullback ke OB atau FVG yang valid\n"
        "- Liquidity sweep sebagai konfirmasi tambahan\n"
        " Untuk SL/TP: gunakan jarak yang realistis. XAUUSD minimum SL 8-15 points, TP1 minimum 1.5× SL distance. RR minimum 1:1.5. Jangan output SL/TP yang terlalu dekat dengan entry."
        "\n\nGRADE & STARS RUBRIC:\n"
        "- SS (stars 5): 88-100% confluence semua faktor align sempurna → MASUK SEKARANG\n"
        "- S  (stars 4-5): 78-88% confluence 4+ faktor align → HIGH CONFIDENCE\n"
        "- A+ (stars 4): 70-80% confluence 3-4 faktor align → VALID TRADE\n"
        "- A  (stars 3): 65-75% confluence 3 faktor → ACCEPTABLE, size kecil\n"
        "- B  (stars 2): 55-65% confluence lemah → TUNGGU konfirmasi lebih lanjut\n"
        "- C  (stars 1): <55% atau tidak ada setup valid → SKIP / NEUTRAL\n"
        "RULE: Jika signal BUY/SELL harus minimum grade B (stars 2). Jika tidak ada setup valid → NEUTRAL + grade C + stars 1.\n"
        "PROBABILITY GUIDANCE: SS=88-95, S=78-88, A+=72-80, A=65-75, B=55-65, C=30-55\n"
    ),

    # ── ULTIMATE — Institutional + macro correlation ──────────────────────────
    "ultimate": (
        "Kamu adalah AI Trading Analyst - Golden AI Strategy (GAS).\n"
        "Mode: INSTITUTIONAL — full SMC + macro correlation + multi-engine.\n\n"
        "GLOBAL RULES:\n"
        "- Gunakan data objektif, no asumsi liar\n"
        "- Jika tidak ada setup valid → output signal: NEUTRAL, order_type: WAIT\n"
        "- Prioritaskan risk management\n"
        "- Hindari overtrading\n"
        "- Output HARUS berupa JSON valid saja — TIDAK ada teks lain di luar JSON\n\n"
        "METHODOLOGY: ICT full stack + macro correlation + institutional order flow.\n\n"
        "ANALYSIS STYLE:\n"
        "- Multi timeframe: D1 (macro) → H4 (struktur) → H1 (setup) → M15 (entry)\n"
        "- SMC full: BOS, CHoCH, OB, FVG, Liquidity, OTE, Kill Zone, AMD\n"
        "- DXY Correlation WAJIB dicek: DXY↑=XAU↓ (SELL), DXY↓=XAU↑ (BUY)\n"
        "- Macro alignment adalah filter utama — jika makro berlawanan, reduce size atau skip\n"
        "- Institutional order flow: identifikasi akumulasi/distribusi smart money\n"
        " Untuk SL/TP: gunakan jarak yang realistis. XAUUSD minimum SL 8-15 points, TP1 minimum 1.5× SL distance. RR minimum 1:1.5. Jangan output SL/TP yang terlalu dekat dengan entry."
        "\n\nGRADE & STARS RUBRIC:\n"
        "- SS (stars 5): 88-100% confluence semua faktor align sempurna → MASUK SEKARANG\n"
        "- S  (stars 4-5): 78-88% confluence 4+ faktor align → HIGH CONFIDENCE\n"
        "- A+ (stars 4): 70-80% confluence 3-4 faktor align → VALID TRADE\n"
        "- A  (stars 3): 65-75% confluence 3 faktor → ACCEPTABLE, size kecil\n"
        "- B  (stars 2): 55-65% confluence lemah → TUNGGU konfirmasi lebih lanjut\n"
        "- C  (stars 1): <55% atau tidak ada setup valid → SKIP / NEUTRAL\n"
        "RULE: Jika signal BUY/SELL harus minimum grade B (stars 2). Jika tidak ada setup valid → NEUTRAL + grade C + stars 1.\n"
        "PROBABILITY GUIDANCE: SS=88-95, S=78-88, A+=72-80, A=65-75, B=55-65, C=30-55\n"
    ),

    # ── ULTRA — Hedge fund mode, scenarios A/B, full confluence ───────────────
    "ultra": (
        "Kamu adalah Autonomous AI Trading Agent - Golden AI Strategy (GAS).\n"
        "Mode: HEDGE FUND — tier tertinggi, full confluence, skenario A/B.\n\n"
        "GLOBAL RULES:\n"
        "- Gunakan data objektif, no asumsi liar\n"
        "- Jika tidak ada setup valid → output signal: NEUTRAL, order_type: WAIT → NO TRADE\n"
        "- Prioritaskan risk management: jaga winrate >60%, hindari drawdown tinggi\n"
        "- Hindari overtrading\n"
        "- Output HARUS berupa JSON valid saja — TIDAK ada teks lain di luar JSON\n\n"
        "METHODOLOGY: ICT institutional + macro full stack + orderflow + AI deep reasoning.\n\n"
        "ANALYSIS STYLE:\n"
        "- Full confluence: SMC + indicator + correlation (DXY, US10Y) + session + news\n"
        "- Wajib output 2 skenario: scenario_1 (primary) + scenario_2 (alternative/invalid)\n"
        "- Tentukan invalidation level yang tepat\n"
        "- Smart score harus mencerminkan kualitas full confluence (0-100)\n"
        "- Self-check sebelum output: apakah RR >1:2? apakah confluence valid? apakah ada news risk?\n"
        "- Psychology check: FOMO, conviction level, mental state, discipline reminder\n"
        "- Pre-trade journal: why entering, setup quality, expectation\n"
        " Untuk SL/TP: gunakan jarak yang realistis. XAUUSD minimum SL 8-15 points, TP1 minimum 1.5× SL distance. RR minimum 1:1.5. Jangan output SL/TP yang terlalu dekat dengan entry."
        "\n\nGRADE & STARS RUBRIC:\n"
        "- SS (stars 5): 88-100% confluence semua faktor align sempurna → MASUK SEKARANG\n"
        "- S  (stars 4-5): 78-88% confluence 4+ faktor align → HIGH CONFIDENCE\n"
        "- A+ (stars 4): 70-80% confluence 3-4 faktor align → VALID TRADE\n"
        "- A  (stars 3): 65-75% confluence 3 faktor → ACCEPTABLE, size kecil\n"
        "- B  (stars 2): 55-65% confluence lemah → TUNGGU konfirmasi lebih lanjut\n"
        "- C  (stars 1): <55% atau tidak ada setup valid → SKIP / NEUTRAL\n"
        "RULE: Jika signal BUY/SELL harus minimum grade B (stars 2). Jika tidak ada setup valid → NEUTRAL + grade C + stars 1.\n"
        "PROBABILITY GUIDANCE: SS=88-95, S=78-88, A+=72-80, A=65-75, B=55-65, C=30-55\n"
    ),
}

# ── Per-market task instructions per plan depth ───────────────────────────────
# GAS Strategy AI official market prompts — per plan × per market
def _market_task_section(market: str, plan_depth: str, indicators: dict, dxy_context: dict) -> str:
    """Return per-market × per-plan task instructions to inject into the prompt."""
    smc = indicators.get("SMC") or {}
    m = (market or "forex").lower()
    sess = smc.get("session", "Unknown")
    dxy_overall = (dxy_context or {}).get("dxy_overall", "UNKNOWN")
    corr_signal = (dxy_context or {}).get("correlation_signal", "NEUTRAL")

    # ── FOREX ─────────────────────────────────────────────────────────────────
    if m in ("forex", "xauusd", "gold"):
        if plan_depth == "essential":
            return (
                "\n\nMARKET: FOREX AI\n"
                "TASK:\n"
                "- Identifikasi trend: bullish / bearish / range\n"
                "- Gunakan RSI, MACD, MA sebagai indikator utama\n"
                "- Cari entry sederhana: breakout atau pullback\n"
                "RULES:\n"
                "- Hindari over-analysis\n"
                "- Hanya 1 setup terbaik\n"
                "- Output singkat, tanpa narasi panjang"
            )
        elif plan_depth == "plus":
            return (
                f"\n\nMARKET: FOREX AI\n"
                f"TASK:\n"
                f"- Trend + RSI + MACD + MA\n"
                f"- Konfirmasi support/resistance\n"
                f"- Validasi entry dengan confluence\n"
                f"EXTRA:\n"
                f"- Cek session aktif: {sess} (Asia/London/NY)\n"
                f"- List minimum 3 faktor confluence yang valid"
            )
        elif plan_depth == "premium":
            return (
                "\n\nMARKET: FOREX AI\n"
                "TASK:\n"
                "- Analisa 3 timeframe: H4 (HTF) → H1 (setup) → M15 (entry)\n"
                "- Deteksi BOS (Break of Structure) dan CHoCH (Change of Character)\n"
                "- Identifikasi Order Block (OB) dan Fair Value Gap (FVG)\n"
                "ENTRY RULE:\n"
                "- Entry dari pullback ke OB atau FVG yang valid\n"
                "- Konfirmasi BOS/CHoCH wajib sebelum entry"
            )
        elif plan_depth in ("ultimate", "ultra"):
            return (
                f"\n\nMARKET: FOREX AI\n"
                f"TASK:\n"
                f"- Multi timeframe: D1 → H4 → H1 → M15\n"
                f"- SMC full: BOS, CHoCH, OB, FVG, Liquidity, OTE, Kill Zone\n"
                f"- Korelasi DXY WAJIB:\n"
                f"  DXY Trend: {dxy_overall}\n"
                f"  Logic: DXY↑ = XAU BEARISH bias | DXY↓ = XAU BULLISH bias\n"
                f"  Confluence Signal: {corr_signal}\n"
                f"LOGIC:\n"
                f"- Jika DXY berlawanan dengan XAU → konfirmasi signal lebih kuat\n"
                f"- Jika DXY searah dengan XAU → CAUTION, reduce size atau skip"
                + (
                    "\nHEDGE FUND EXTRA:\n"
                    "- Tambahkan korelasi US10Y jika relevan\n"
                    "- Tentukan scenario A (primary) dan scenario B (alternative/invalidation)\n"
                    "- Output invalidation level yang spesifik"
                    if plan_depth == "ultra" else ""
                )
            )

    # ── CRYPTO / BINANCE ──────────────────────────────────────────────────────
    elif m in ("crypto", "binance", "btc", "eth"):
        if plan_depth == "essential":
            return (
                "\n\nMARKET: BINANCE AI (CRYPTO)\n"
                "TASK:\n"
                "- Deteksi momentum: volume + RSI\n"
                "- Cari breakout atau continuation signal\n"
                "EXTRA:\n"
                "- Cek volume spike — wajib ada konfirmasi volume"
            )
        elif plan_depth == "plus":
            return (
                "\n\nMARKET: BINANCE AI (CRYPTO)\n"
                "TASK:\n"
                "- Momentum + volume + market structure\n"
                "- Deteksi fake breakout\n"
                "EXTRA:\n"
                "- Volume spike validation wajib\n"
                "- Identifikasi apakah breakout valid atau trap"
            )
        elif plan_depth == "premium":
            return (
                "\n\nMARKET: BINANCE AI (CRYPTO)\n"
                "TASK:\n"
                "- Market structure: BOS, CHoCH, OB, FVG\n"
                "- Liquidity analysis: sweep valid atau fake\n"
                "- Volume confirmation wajib\n"
                "EXTRA:\n"
                "- Deteksi trap market (fake breakout + liquidity grab)\n"
                "- Identifikasi apakah ini accumulation atau distribution"
            )
        elif plan_depth in ("ultimate", "ultra"):
            return (
                "\n\nMARKET: BINANCE AI (CRYPTO)\n"
                "TASK:\n"
                "- BTC Dominance: naik = altcoin bearish, turun = altcoin bullish\n"
                "- ETH correlation untuk major crypto pairs\n"
                "- Liquidity sweep analysis — institutional level\n"
                "- Volume: deteksi whale accumulation atau distribution\n"
                "EXTRA:\n"
                "- Deteksi whale manipulation via volume + liquidity sweep abnormal\n"
                "- Output btc_dominance_impact: bullish/bearish/neutral + penjelasan"
                + (
                    "\nHEDGE FUND EXTRA:\n"
                    "- Orderflow analysis: bid/ask pressure\n"
                    "- Deteksi whale manipulation level institutional\n"
                    "- Scenario A/B wajib"
                    if plan_depth == "ultra" else ""
                )
            )

    # ── STOCK IDX / IHSG ──────────────────────────────────────────────────────
    elif m in ("stock", "stock_idx", "idx", "ihsg"):
        if plan_depth == "essential":
            return (
                "\n\nMARKET: STOCK IDX\n"
                "TASK:\n"
                "- Cek trend + support/resistance\n"
                "- Fokus daily trend\n"
                "RULES:\n"
                "- Hindari saham illiquid (volume rendah)\n"
                "- Hanya rekomendasikan saham dengan likuiditas cukup"
            )
        elif plan_depth == "plus":
            return (
                "\n\nMARKET: STOCK IDX\n"
                "TASK:\n"
                "- Trend + volume + breakout detection\n"
                "- Volume confirmation wajib\n"
                "RULES:\n"
                "- Hindari sideways market\n"
                "- Cek likuiditas saham sebelum rekomendasikan entry"
            )
        elif plan_depth == "premium":
            return (
                "\n\nMARKET: STOCK IDX\n"
                "TASK:\n"
                "- Market structure: breakout valid atau false breakout\n"
                "- Volume strong confirmation wajib\n"
                "- Identifikasi support/resistance struktural\n"
                "EXTRA:\n"
                "- Konfirmasi breakout dengan volume spike\n"
                "- Cek apakah saham dalam uptrend/downtrend struktural"
            )
        elif plan_depth in ("ultimate", "ultra"):
            return (
                "\n\nMARKET: STOCK IDX\n"
                "TASK:\n"
                "- IHSG overall direction sebagai leading indicator\n"
                "- Global sentiment: korelasi dengan US market (S&P500/Nasdaq)\n"
                "- Sector rotation: sektor leading vs lagging\n"
                "- Institutional flow: akumulasi atau distribusi\n"
                "EXTRA:\n"
                "- Output ihsg_correlation: bullish/bearish/neutral + penjelasan\n"
                "- Identifikasi sektor yang sedang dalam fase akumulasi"
                + (
                    "\nHEDGE FUND EXTRA:\n"
                    "- Institutional accumulation/distribution pattern\n"
                    "- Smart money flow tracking\n"
                    "- Scenario A/B wajib"
                    if plan_depth == "ultra" else ""
                )
            )

    # ── MEMECOIN ──────────────────────────────────────────────────────────────
    elif m in ("meme", "memecoin", "memecoins"):
        if plan_depth == "essential":
            return (
                "\n\nMARKET: MEMECOIN\n"
                "TASK:\n"
                "- Deteksi awal pump: volume + volatility spike\n"
                "- Identifikasi momentum awal\n"
                "RULES:\n"
                "- HIGH RISK WARNING wajib ada di output\n"
                "- SL ketat mandatory"
            )
        elif plan_depth == "plus":
            return (
                "\n\nMARKET: MEMECOIN\n"
                "TASK:\n"
                "- Early trend detection\n"
                "- Liquidity + volume spike analysis\n"
                "RULES:\n"
                "- Volatility tinggi — SL ketat wajib\n"
                "- Identifikasi apakah volume spike organik atau bot\n"
                "- Warning: VOLATILE wajib ada di output"
            )
        elif plan_depth == "premium":
            return (
                "\n\nMARKET: MEMECOIN\n"
                "TASK:\n"
                "- Smart money entry via liquidity zone valid\n"
                "- Deteksi rug pull risk\n"
                "- Analisa holder distribution jika data tersedia\n"
                "EXTRA OUTPUT WAJIB:\n"
                "- scam_risk_score: 0-100 (100 = pasti rug pull)\n"
                "RULES:\n"
                "- Risk medium/high harus tercantum di output"
            )
        elif plan_depth in ("ultimate", "ultra"):
            return (
                "\n\nMARKET: MEMECOIN\n"
                "TASK:\n"
                "- Smart money flow tracking\n"
                "- Wallet distribution analysis (jika tersedia)\n"
                "- Pump probability estimation\n"
                "EXTRA OUTPUT WAJIB:\n"
                "- pump_probability: 0-100\n"
                "- rug_risk_pct: 0-100"
                + (
                    "\nANTI RUGPULL SYSTEM (ULTRA):\n"
                    "- Liquidity lock status check\n"
                    "- Holder distribution: concentrated = high rug risk\n"
                    "- Volume spike abnormal detection (bot activity)\n"
                    "- EXTRA OUTPUT: trust_score (0-100), rugpull_risk (low/medium/high)"
                    if plan_depth == "ultra" else ""
                )
            )

    # ── POLYMARKET ────────────────────────────────────────────────────────────
    elif m in ("poly", "polymarket", "prediction"):
        if plan_depth == "essential":
            return (
                "\n\nMARKET: POLYMARKET\n"
                "TASK:\n"
                "- Analisa probabilitas YES/NO\n"
                "- Gunakan trend sentiment sederhana\n"
                "OUTPUT WAJIB:\n"
                "- probability_yes: 0-100\n"
                "- probability_no: 0-100"
            )
        elif plan_depth == "plus":
            return (
                "\n\nMARKET: POLYMARKET\n"
                "TASK:\n"
                "- Probability + market sentiment analysis\n"
                "- Basic news impact assessment\n"
                "OUTPUT WAJIB:\n"
                "- probability_yes: 0-100\n"
                "- probability_no: 0-100\n"
                "- sentiment: positive/negative/neutral"
            )
        elif plan_depth == "premium":
            return (
                "\n\nMARKET: POLYMARKET\n"
                "TASK:\n"
                "- Probability weighted analysis\n"
                "- Sentiment + trend alignment\n"
                "OUTPUT WAJIB:\n"
                "- probability_yes: 0-100\n"
                "- probability_no: 0-100\n"
                "- edge_score: 0-100 (seberapa kuat edge prediction ini)"
            )
        elif plan_depth in ("ultimate", "ultra"):
            return (
                "\n\nMARKET: POLYMARKET\n"
                "TASK:\n"
                "- Probability + liquidity + volume weighted\n"
                "- Crowd bias vs smart money divergence\n"
                "- Multi-factor prediction: sentiment + volume + price movement\n"
                "OUTPUT WAJIB:\n"
                "- final_probability: 0-100\n"
                "- market_bias: YES atau NO\n"
                "- edge_score: 0-100"
                + (
                    "\nHEDGE FUND EXTRA:\n"
                    "- Multi-model AI consensus\n"
                    "- Confidence score weighted\n"
                    "- Output: confidence_score, ai_consensus"
                    if plan_depth == "ultra" else ""
                )
            )

    return ""


def _output_schema(plan_depth: str, market: str) -> str:
    """Return the JSON output schema string for the given plan depth and market."""
    m = (market or "forex").lower()
    is_poly = m in ("poly", "polymarket", "prediction")
    is_meme = m in ("meme", "memecoin", "memecoins")
    is_crypto = m in ("crypto", "binance", "btc", "eth")
    is_stock = m in ("stock", "stock_idx", "idx", "ihsg")

    # ── Base fields (all plans) ───────────────────────────────────────────────
    if is_poly:
        base = """\
{
  "signal": "YES" atau "NO" atau "NEUTRAL",
  "probability_yes": <int 0-100>,
  "probability_no": <int 0-100>,
  "confidence": <int 0-100>,
  "grade": "SS" atau "S" atau "A+" atau "A" atau "B" atau "C",
  "trigger": "<1 kalimat singkat>",
  "reasoning": "<penjelasan>"""
    else:
        base = """\
{
  "signal": "BUY" atau "SELL" atau "NEUTRAL",
  "order_type": "BUY NOW" atau "SELL NOW" atau "BUY LIMIT" atau "SELL LIMIT" atau "BUY STOP" atau "SELL STOP" atau "WAIT",
  "probability": <int 0-100>,
  "grade": "SS" atau "S" atau "A+" atau "A" atau "B" atau "C",
  "stars": <int 1-5>,
  "entry": <float>,
  "sl": <float>,
  "tp1": <float>,
  "tp2": <float>,
  "style": "SCALPING" atau "INTRADAY" atau "SWING",
  "trigger": "<1 kalimat>",
  "reasoning": "<2-3 kalimat>"""

    if plan_depth == "essential":
        if is_poly:
            return base + '\n}'
        extra = ',\n  "high_risk_warning": "<peringatan risiko>"' if is_meme else ""
        return base + extra + '\n}'

    # ── Plus adds ──────────────────────────────────────────────────────────────
    plus_fields = ',\n  "tp3": <float>' if not is_poly else ""
    plus_fields += ',\n  "session": "<sesi aktif>"'
    plus_fields += ',\n  "setup": "<setup type>"'
    plus_fields += ',\n  "momentum": "<strong/weak/neutral>"'
    plus_fields += ',\n  "confluence": ["<faktor 1>", "<faktor 2>", "<faktor 3>"]'
    if is_crypto:
        plus_fields += ',\n  "volume_spike": <bool>'
        plus_fields += ',\n  "fake_breakout_risk": "<low/medium/high>"'
    if is_poly:
        plus_fields += ',\n  "sentiment": "<positive/negative/neutral>"'

    if plan_depth == "plus":
        return base + plus_fields + '\n}'

    # ── Premium adds (SMC) ────────────────────────────────────────────────────
    premium_fields = plus_fields
    premium_fields += ',\n  "smc_structure": "<HH-HL / LH-LL / BOS / CHoCH>"'
    premium_fields += ',\n  "liquidity_status": "<swept/intact>"'
    premium_fields += ',\n  "ob_fvg": "<OB/FVG zone yang digunakan>"'
    premium_fields += ',\n  "score": <int 0-100>'
    premium_fields += ',\n  "key_levels": {"support": <float>, "resistance": <float>}'
    premium_fields += ',\n  "trading_plan": "<3-4 kalimat entry + TP management>"'
    if is_meme:
        premium_fields += ',\n  "scam_risk_score": <int 0-100>'
    if is_poly:
        premium_fields += ',\n  "edge_score": <int 0-100>'

    if plan_depth == "premium":
        return base + premium_fields + '\n}'

    # ── Ultimate adds (macro + correlation) ───────────────────────────────────
    ultimate_fields = premium_fields
    ultimate_fields += ',\n  "htf_analysis": "<HTF D1/H4 trend dan key level>"'
    ultimate_fields += ',\n  "ltf_entry": "<LTF M15/M5 konfirmasi entry>"'
    ultimate_fields += ',\n  "edge_score": <int 0-100>'
    ultimate_fields += ',\n  "risk_management": "<lot sizing, SL pips, portfolio heat>"'
    ultimate_fields += ',\n  "invalidation": "<kondisi batal sinyal>"'
    if not is_poly and not is_meme:
        if m in ("forex", "xauusd", "gold"):
            ultimate_fields += ',\n  "dxy_confirmation": "<CONFIRMED/CAUTION/NO_DATA + penjelasan>"'
        elif is_crypto:
            ultimate_fields += ',\n  "btc_dominance_impact": "<bullish/bearish/neutral + penjelasan>"'
        elif is_stock:
            ultimate_fields += ',\n  "ihsg_correlation": "<bullish/bearish/neutral + penjelasan>"'
    if is_meme:
        ultimate_fields += ',\n  "pump_probability": <int 0-100>'
        ultimate_fields += ',\n  "rug_risk_pct": <int 0-100>'
    if is_poly:
        ultimate_fields += ',\n  "final_probability": <int 0-100>'
        ultimate_fields += ',\n  "market_bias": "YES" atau "NO"'

    if plan_depth == "ultimate":
        return base + ultimate_fields + '\n}'

    # ── Ultra adds (hedge fund scenarios) ─────────────────────────────────────
    ultra_fields = ultimate_fields
    ultra_fields += ',\n  "scenario_1": "<primary skenario — kondisi dan target>"'
    ultra_fields += ',\n  "scenario_2": "<alternative skenario — kondisi dan invalidasi>"'
    ultra_fields += ',\n  "smart_score": <int 0-100>'
    ultra_fields += ',\n  "observation": "<hal kritis yang perlu diobservasi>"'
    ultra_fields += ',\n  "journal_entry": "<pre-trade journal>"'
    ultra_fields += ',\n  "psychology": "<mindset check, FOMO, discipline>"'
    if is_meme:
        ultra_fields += ',\n  "trust_score": <int 0-100>'
        ultra_fields += ',\n  "rugpull_risk": "<low/medium/high>"'
    if is_poly:
        ultra_fields += ',\n  "confidence_score": <int 0-100>'
        ultra_fields += ',\n  "ai_consensus": "<summary AI reasoning>"'

    return base + ultra_fields + '\n}'


def _build_agent_prompt(pair: str, timeframe: str, indicators: dict, current_price: float,
                         dxy_context: dict = None, market: str = "forex") -> tuple[str, str]:
    """
    AI Agent prompt (Feature 19) — Autonomous Trading AI Agent.
    Role: picks best setup from all data, evaluates quality, outputs with self-check.
    Maps to model_tier='agent' (Claude Opus 4.6), plan depth: ultra.
    """
    smc = indicators.get("SMC") or {}
    rec = indicators.get("recommendation", "NEUTRAL")
    conf = indicators.get("confidence", 0)
    rsi = indicators.get("RSI", {}).get("value", 50)
    dxy_overall = (dxy_context or {}).get("dxy_overall", "N/A")
    corr = (dxy_context or {}).get("correlation_signal", "N/A")

    system = (
        "Kamu adalah Autonomous AI Trading Agent - Golden AI Strategy (GAS).\n"
        "Role: Agen trading otomatis yang memilih setup terbaik dari semua data yang tersedia.\n\n"
        "AGENT RULES:\n"
        "- Jika tidak ada setup valid → output signal: NEUTRAL, order_type: WAIT → NO TRADE\n"
        "- Jaga winrate target >60%, hindari drawdown tinggi\n"
        "- Risk/Reward minimum 1:2 untuk setiap trade yang direkomendasikan\n"
        "- Validasi confluence sebelum output: indikator + SMC + makro harus align\n"
        "- Evaluasi kualitas setup: grade A+/A = valid, B = tunggu, C = skip\n\n"
        "SELF-CHECK SEBELUM OUTPUT:\n"
        "1. Apakah RR > 1:2? Jika tidak → grade C, pertimbangkan WAIT\n"
        "2. Apakah confluence valid (minimal 3 faktor)? Jika tidak → NEUTRAL\n"
        "3. Apakah ada news risk? Jika ya → catat di observation\n"
        "4. Apakah makro (DXY/BTC DOM) mendukung? Jika berlawanan → reduce size atau skip\n"
        "5. FOMO check: apakah entry sudah terlambat? Jika ya → WAIT next setup\n\n"
        "Output HARUS berupa JSON valid saja — TIDAK ada teks lain di luar JSON.\n"
        " Untuk SL/TP: gunakan jarak yang realistis. XAUUSD minimum SL 8-15 points, TP1 minimum 1.5× SL distance. RR minimum 1:1.5. Jangan output SL/TP yang terlalu dekat dengan entry."
    )

    mkt_task = _market_task_section(market, "ultra", indicators, dxy_context or {})
    smc_bos = "YES" if smc.get("bos") else "no"
    smc_choch = "YES" if smc.get("choch") else "no"
    amd = smc.get("amd_phase", "unknown")
    liq = "SWEPT" if smc.get("liquidity_swept") else "intact"

    user = (
        f"=== AGENT DATA INPUT ===\n"
        f"Pair: {pair} | TF: {timeframe} | Price: {current_price}\n"
        f"Market: {market.upper()}\n\n"
        f"INDICATOR ENGINE:\n"
        f"- RSI(14): {rsi:.2f} ({'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Normal'})\n"
        f"- MACD: {format_dict(indicators.get('MACD', {}))}\n"
        f"- EMA: {format_dict(indicators.get('EMA', {}))}\n"
        f"- ADX: {format_dict(indicators.get('ADX', {}))}\n"
        f"- BB: {format_dict(indicators.get('BB', {}))}\n"
        f"- System Rec: {rec} ({conf}%)\n\n"
        f"SMC ENGINE:\n"
        f"- Bias: {smc.get('bias','N/A')} | BOS: {smc_bos} | CHoCH: {smc_choch}\n"
        f"- Liquidity: {liq} | AMD Phase: {amd}\n"
        f"- SMC Score: {smc.get('smc_score',0)}/100\n"
        f"- SMC Entry: {smc.get('smc_entry','N/A')} | SL: {smc.get('smc_sl','N/A')}\n\n"
        f"MACRO CORRELATION:\n"
        f"- DXY: {dxy_overall} | Confluence Signal: {corr}\n"
        f"{mkt_task}\n\n"
        f"AGENT SELF-CHECK:\n"
        f"- Evaluasi apakah setup ini layak untuk ditrading\n"
        f"- Jika tidak ada setup valid → output NEUTRAL / WAIT\n"
        f"- Hitung smart_score berdasarkan full confluence quality\n\n"
        f"Output JSON saja:\n"
        f"{_output_schema('ultra', market)}"
    )
    return system, user


# ── Tiered Signal Analysis ────────────────────────────────────────────────────

def _build_signal_prompt(pair: str, timeframe: str, indicators: dict, current_price: float,
                          dxy_context: dict = None, plan_depth: str = "premium", market: str = "forex") -> tuple[str, str]:
    """
    Build per-plan × per-market signal prompt.
    Plan depths: essential | plus | premium | ultimate | ultra
    Markets: forex | crypto | stock | meme | poly
    Data sources: Indicator Engine + SMC Engine + DXY Correlation (depth-gated)
    """
    # ── Common indicator data ──────────────────────────────────────────────────
    rsi     = indicators.get("RSI", {}).get("value", 50)
    macd    = indicators.get("MACD", {})
    ema     = indicators.get("EMA", {})
    adx     = indicators.get("ADX", {})
    bb      = indicators.get("BB", {})
    rec     = indicators.get("recommendation", "NEUTRAL")
    conf    = indicators.get("confidence", 0)
    setup   = indicators.get("setup_type", "Unknown")
    conf_sc = indicators.get("confluence_score", conf)

    # ── SMC Engine data ──────────────────────────────────────────────────────
    smc = indicators.get("SMC") or {}
    smc_bias    = smc.get("bias", "N/A")
    smc_struct  = smc.get("structure", "")
    smc_bos     = "YES" if smc.get("bos") else "no"
    smc_choch   = "YES" if smc.get("choch") else "no"
    smc_score   = smc.get("smc_score", 0)
    smc_action  = smc.get("smc_action", "WAIT")
    liq_swept   = "SWEPT" if smc.get("liquidity_swept") else "intact"
    liq_pools   = smc.get("liquidity_pools", 0)
    ote_active  = "YES (61.8-78.6%)" if smc.get("ote_zone") else "no"
    ote_type    = smc.get("ote_type", "")
    kill_zone   = "ACTIVE" if smc.get("kill_zone") else "outside"
    amd_phase   = smc.get("amd_phase", "unknown")
    session     = smc.get("session", "")
    obs         = smc.get("order_blocks", [])
    fvg_count   = smc.get("fvg_count", 0)
    smc_entry   = smc.get("smc_entry")
    smc_sl      = smc.get("smc_sl")
    smc_tp      = smc.get("smc_tp")
    smc_reason  = smc.get("smc_reason", "")

    ob_lines = ""
    for ob in (obs or [])[:2]:
        ob_lines += f"\n  OB {ob.get('type','?')}: entry={ob.get('entry')} sl={ob.get('sl')} tp={ob.get('tp')} grade={ob.get('strength','?')}"

    # ── Build system identity ─────────────────────────────────────────────────
    system = _SYSTEM_IDENTITY.get(plan_depth, _SYSTEM_IDENTITY["premium"])

    # ── Build input sections based on plan depth ──────────────────────────────
    # Essential: indicators only (no SMC, no DXY)
    # Plus: indicators + session
    # Premium+: full indicators + SMC
    # Ultimate+: full stack + DXY/macro correlation
    # Ultra: everything + hedge fund context

    indicator_section = (
        f"INDICATOR ENGINE:\n"
        f"- RSI(14): {rsi:.2f} ({'⚠️ Overbought' if rsi > 70 else '⚠️ Oversold' if rsi < 30 else 'Normal'})\n"
        f"- MACD: {format_dict(macd)}\n"
        f"- EMA: {format_dict(ema)}\n"
        f"- TA Rec: {rec} ({conf}%)"
    )
    if plan_depth not in ("essential",):
        indicator_section += f"\n- ADX: {format_dict(adx)}\n- Bollinger Bands: {format_dict(bb)}"

    smc_section = ""
    if plan_depth in ("premium", "ultimate", "ultra"):
        if smc:
            smc_section = (
                f"\nSMC ENGINE:\n"
                f"- Bias: {smc_bias} | Structure: {smc_struct}\n"
                f"- BOS: {smc_bos} | CHoCH: {smc_choch}\n"
                f"- Liquidity: {liq_swept} | Pools: {liq_pools}\n"
                f"- OTE Zone: {ote_active} {ote_type}\n"
                f"- Kill Zone: {kill_zone} | Session: {session}\n"
                f"- AMD Phase: {amd_phase} | FVG Count: {fvg_count}\n"
                f"- Order Blocks:{ob_lines if ob_lines else ' none'}\n"
                f"- SMC Action: {smc_action} | Score: {smc_score}/100\n"
                f"- SMC Entry: {smc_entry} | SL: {smc_sl} | TP: {smc_tp}\n"
                f"- SMC Reason: {smc_reason}"
            )
        else:
            smc_section = "\nSMC ENGINE: data tidak tersedia (gunakan indicator-only)"

    dxy_section = ""
    if plan_depth in ("ultimate", "ultra") and dxy_context and isinstance(dxy_context, dict):
        dxy_overall = dxy_context.get("dxy_overall", "NEUTRAL")
        corr_signal = dxy_context.get("correlation_signal", "NEUTRAL")
        xau_overall = dxy_context.get("xau_overall", "NEUTRAL")
        mtf_summary = dxy_context.get("mtf_summary", {})
        style_nm    = dxy_context.get("style", "intraday")
        dxy_note    = dxy_context.get("note", "")
        mtf_lines   = " | ".join(f"{tf}:{tr}" for tf, tr in mtf_summary.items()) if mtf_summary else "no data"
        dxy_section = (
            f"\nDXY CORRELATION (MANDATORY — ultimate/ultra):\n"
            f"- DXY Trend: {dxy_overall} → DXY↑=XAU↓ BEARISH, DXY↓=XAU↑ BULLISH\n"
            f"- XAU Overall: {xau_overall} | Confluence: {corr_signal}\n"
            f"- Multi-TF ({style_nm.upper()}): {mtf_lines}\n"
            f"- Rule: {dxy_note}"
        )

    # Plus adds session context
    session_section = ""
    if plan_depth in ("plus",) and smc:
        session_section = f"\nSESSION CONTEXT: {session or 'Unknown'} | AMD Phase: {amd_phase}"

    # Market-specific analysis injection
    market_section = _market_task_section(market, plan_depth, indicators, dxy_context or {})

    # Ultra: hedge fund scenario instruction
    ultra_section = ""
    if plan_depth == "ultra":
        ultra_section = (
            "\nHEDGE FUND RULES:"
            "\n- Wajib output 2 skenario (primary + alternative)"
            "\n- Tentukan invalidation level yang tepat"
            "\n- Smart score harus mencerminkan kualitas full confluence"
            "\n- Jika tidak ada setup valid → output signal: NEUTRAL, order_type: WAIT"
        )

    # ── Assemble user prompt ──────────────────────────────────────────────────
    user = (
        f"=== DATA INPUT ===\n"
        f"Pair: {pair} | TF: {timeframe} | Price: {current_price}\n"
        f"Setup: {setup} | Confluence Score: {conf_sc}/100\n\n"
        f"{indicator_section}"
        f"{session_section}"
        f"{smc_section}"
        f"{dxy_section}"
        f"{market_section}"
        f"{ultra_section}"
        f"\n\nOutput JSON saja, tidak ada teks lain:\n"
        f"{_output_schema(plan_depth, market)}"
    )

    return system, user


def _build_scanner_pair_prompt(pair: str, timeframe: str, indicators: dict, current_price: float) -> tuple[str, str]:
    """Build system + user prompt for scanner per-pair (concise version)."""
    rsi = indicators.get("RSI", {}).get("value", 50)
    rec = indicators.get("recommendation", "NEUTRAL")
    conf = indicators.get("confidence", 0)
    macd_sig = indicators.get("MACD", {}).get("signal", "neutral")
    ema_sig = indicators.get("EMA", {}).get("signal", "neutral")
    adx_str = indicators.get("ADX", {}).get("strength", "weak")

    system = (
        "Kamu adalah AI Scanner GAS Strategy AI. "
        "Analisa pair dan hasilkan sinyal dalam JSON valid saja — tidak ada teks lain. "
        "Untuk SL/TP: gunakan jarak yang realistis. XAUUSD minimum SL 8-15 points dari entry, "
        "TP1 minimum 1.5× SL distance. RR minimum 1:1.5. Jangan output SL/TP yang terlalu dekat dengan entry."
    )
    user = f"""Pair: {pair} | TF: {timeframe} | Price: {current_price}
RSI: {rsi:.1f} | MACD: {macd_sig} | EMA: {ema_sig} | ADX: {adx_str} | System: {rec} ({conf}%)

JSON saja:
{{
  "signal": "BUY" atau "SELL" atau "NEUTRAL",
  "order_type": "BUY NOW" atau "SELL NOW" atau "BUY LIMIT" atau "SELL LIMIT" atau "WAIT",
  "probability": <int 0-100>,
  "confidence": <int 0-100>,
  "grade": "SS" atau "S" atau "A+" atau "A" atau "B" atau "C",
  "stars": <int 1-5>,
  "entry": <float>,
  "sl": <float>,
  "tp1": <float>,
  "tp2": <float>,
  "tp3": <float>,
  "rr": "<string>",
  "trigger": "<1 kalimat singkat>",
  "reasoning": "<1 kalimat>"
}}"""
    return system, user


async def analyze_signal_tiered(
    pair: str, timeframe: str, indicators: dict, current_price: float,
    model_tier: str = "basic", dxy_context: dict = None, market: str = "forex",
) -> dict:
    """
    Generate per-plan × per-market signal using the specified tier's AI model.
    Tier: basic(essential) | advanced(plus) | pro(premium) | ultra(ultimate) | gpt(ultimate) | agent(ultra)
    Market: forex | crypto | stock | meme | poly
    """
    tier_cfg = MODEL_TIERS.get(model_tier, MODEL_TIERS["basic"])
    model = tier_cfg["model"]
    temperature = tier_cfg["temperature"]
    max_tokens = tier_cfg["max_tokens"]
    label = tier_cfg["label"]
    plan_depth = TIER_TO_PLAN_DEPTH.get(model_tier, "premium")

    # Agent tier uses its own dedicated autonomous prompt
    if model_tier == "agent":
        system, user = _build_agent_prompt(
            pair, timeframe, indicators, current_price,
            dxy_context=dxy_context, market=market,
        )
    else:
        system, user = _build_signal_prompt(
            pair, timeframe, indicators, current_price,
            dxy_context=dxy_context, plan_depth=plan_depth, market=market,
        )

    ai_text = await _ask_openrouter_model(model, system, user, temperature, max_tokens)
    result = _parse_json(ai_text)

    rec = indicators.get("recommendation", "NEUTRAL")
    conf = indicators.get("confidence", 0)

    if result and result.get("signal") in ("BUY", "SELL", "NEUTRAL", "YES", "NO"):
        result["model"] = label
        result["model_tier"] = model_tier
        result["plan_depth"] = plan_depth
        result["market"] = market
        result["pair"] = pair
        result["timeframe"] = timeframe
        result["current_price"] = current_price

        # ── Patch null/zero SL-TP values that AI sometimes omits ─────────────
        sig_dir = result.get("signal", "NEUTRAL")
        entry_val = result.get("entry") or current_price
        # For NEUTRAL: use SELL direction if RSI overbought, else BUY — just for levels
        if sig_dir == "NEUTRAL":
            rsi_val = (indicators.get("RSI") or {}).get("value", 50)
            sig_for_levels = "SELL" if rsi_val > 55 else "BUY"
        else:
            sig_for_levels = sig_dir
        needs_patch = (
            not result.get("sl") or result.get("sl") == 0 or
            not result.get("tp1") or result.get("tp1") == 0
        )
        if needs_patch:
            _, sl_c, tp1_c, tp2_c, tp3_c, rr_c = _compute_sltp(indicators, float(entry_val), sig_for_levels)
            if not result.get("sl") or result.get("sl") == 0:
                result["sl"] = sl_c
            if not result.get("tp1") or result.get("tp1") == 0:
                result["tp1"] = tp1_c
            if not result.get("tp2") or result.get("tp2") == 0:
                result["tp2"] = tp2_c
            if not result.get("tp3") or result.get("tp3") == 0:
                result["tp3"] = tp3_c
            if not result.get("rr") or result.get("rr") == "N/A":
                result["rr"] = rr_c
        if not result.get("entry") or result.get("entry") == 0:
            result["entry"] = round(float(current_price), 5)

        # Enforce minimum RR and SL distance
        result["entry"], result["sl"], result["tp1"], result["tp2"], result["tp3"] = _enforce_min_rr(
            result.get("entry", current_price),
            result.get("sl", 0),
            result.get("tp1", 0),
            result.get("tp2", 0),
            result.get("tp3", 0),
            result.get("signal", "NEUTRAL"),
            pair,
        )
        # Recalculate RR
        e, s = result.get("entry", current_price), result.get("sl")
        t2 = result.get("tp2")
        if s and t2 and s != e:
            result["rr"] = f"1:{abs(float(t2)-float(e))/abs(float(e)-float(s)):.1f}"

        return result

    # ── Structured fallback: compute real SL/TP from indicator data ──────────
    sig = rec if rec in ("BUY", "SELL") else "NEUTRAL"
    sig_dir_fb = sig if sig != "NEUTRAL" else "BUY"
    entry, sl, tp1, tp2, tp3, rr = _compute_sltp(indicators, current_price, sig_dir_fb)
    # Apply min RR enforcement on fallback too
    entry, sl, tp1, tp2, tp3 = _enforce_min_rr(entry, sl, tp1, tp2, tp3, sig_dir_fb, pair)
    if sl and tp2 and sl != entry:
        rr = f"1:{abs(float(tp2)-float(entry))/abs(float(entry)-float(sl)):.1f}"
    smc = indicators.get("SMC") or {}
    reasoning = _build_technical_text(pair, timeframe, indicators, current_price)
    return {
        "signal": sig,
        "order_type": ("BUY LIMIT" if sig == "BUY" else "SELL LIMIT") if sig != "NEUTRAL" else "WAIT",
        "probability": conf,
        "grade": "SS" if conf >= 88 else "S" if conf >= 78 else "A+" if conf >= 70 else "A" if conf >= 65 else "B" if conf >= 55 else "C",
        "stars": 5 if conf >= 88 else 4 if conf >= 70 else 3 if conf >= 65 else 2 if conf >= 55 else 1,
        "confidence": conf,
        "entry": entry, "sl": sl, "tp1": tp1, "tp2": tp2, "tp3": tp3,
        "rr": rr,
        "lot_suggestion": 0.01,
        "style": "SCALPING" if timeframe in ("M5", "M15") else "INTRADAY" if timeframe in ("H1", "H4") else "SWING",
        "session": smc.get("session", "London"),
        "trigger": f"Konfluensi TA: {rec} {conf}% | RSI {indicators.get('RSI',{}).get('value',50):.0f} | SMC {smc.get('amd_phase','N/A')}",
        "reasoning": reasoning,
        "trading_plan": f"Entry di {entry}, SL di {sl} (BB/SMC-based). Ambil profit parsial di TP1 {tp1}, target TP2 {tp2}.",
        "key_levels": {
            "support": indicators.get("BB", {}).get("lower") or indicators.get("EMA", {}).get("ema50"),
            "resistance": indicators.get("BB", {}).get("upper") or indicators.get("EMA", {}).get("ema20"),
        },
        "invalidation": f"Close {'di atas' if sig == 'SELL' else 'di bawah'} SL {sl}",
        "model": label,
        "model_tier": model_tier,
        "plan_depth": plan_depth,
        "pair": pair,
        "timeframe": timeframe,
        "current_price": current_price,
        "ai_source": "indicator-fallback",
    }


async def analyze_pair_scanner_tiered(
    pair: str, timeframe: str, indicators: dict, current_price: float,
    model_tier: str = "basic"
) -> dict:
    """Per-pair rich signal for batch scanner using selected tier model."""
    tier_cfg = MODEL_TIERS.get(model_tier, MODEL_TIERS["basic"])
    model = tier_cfg["model"]
    temperature = tier_cfg["temperature"]
    label = tier_cfg["label"]

    system, user = _build_scanner_pair_prompt(pair, timeframe, indicators, current_price)
    ai_text = await _ask_openrouter_model(model, system, user, temperature, 500)
    result = _parse_json(ai_text)

    rec = indicators.get("recommendation", "NEUTRAL")
    conf = indicators.get("confidence", 0)

    if result and result.get("signal") in ("BUY", "SELL", "NEUTRAL"):
        result.update({
            "pair": pair, "price": current_price, "timeframe": timeframe,
            "model": label, "model_tier": model_tier,
        })
        return result

    sig = rec if rec in ("BUY", "SELL") else "NEUTRAL"
    entry, sl, tp1, tp2, tp3, rr = _compute_sltp(indicators, current_price, sig if sig != "NEUTRAL" else "BUY")
    return {
        "pair": pair, "price": current_price, "timeframe": timeframe,
        "signal": sig,
        "order_type": ("BUY LIMIT" if sig == "BUY" else "SELL LIMIT") if sig != "NEUTRAL" else "WAIT",
        "probability": conf, "confidence": conf,
        "grade": "SS" if conf >= 88 else "S" if conf >= 78 else "A+" if conf >= 70 else "A" if conf >= 65 else "B" if conf >= 55 else "C",
        "stars": 5 if conf >= 88 else 4 if conf >= 70 else 3 if conf >= 65 else 2 if conf >= 55 else 1,
        "entry": entry, "sl": sl, "tp1": tp1, "tp2": tp2, "tp3": tp3, "rr": rr,
        "trigger": f"TA: {rec} {conf}% | RSI {indicators.get('RSI',{}).get('value',50):.0f}",
        "reasoning": _build_technical_text(pair, timeframe, indicators, current_price)[:200],
        "model": label, "model_tier": model_tier,
        "ai_source": "indicator-fallback",
    }


# ── Legacy wrappers (kept for backward-compat) ────────────────────────────────

async def analyze_signal(pair: str, timeframe: str, indicators: dict, current_price: float) -> dict:
    """Backward-compat: calls basic tier."""
    return await analyze_signal_tiered(pair, timeframe, indicators, current_price, "basic")


async def analyze_pair_for_scanner(pair: str, timeframe: str, indicators: dict, current_price: float) -> dict:
    """Backward-compat: calls basic tier scanner."""
    return await analyze_pair_scanner_tiered(pair, timeframe, indicators, current_price, "basic")


# ── Premium Signal Analysis — Kimi 2.5 (legacy, DISABLED — use tiered above) ──

async def _analyze_signal_kimi_legacy(pair: str, timeframe: str, indicators: dict, current_price: float) -> dict:
    """
    Legacy Kimi signal — disabled/renamed to avoid overriding backward-compat wrapper above.
    """
    system = (
        "Kamu adalah AI Signal Generator premium untuk platform GAS Strategy AI. "
        "Hasilkan sinyal trading berkualitas tinggi berbasis data teknikal nyata. "
        "Output HARUS berupa JSON valid saja. Gunakan ICT/SMC methodology: "
        "identifikasi order flow, OB, FVG, liquidity, dan struktur market."
    )

    rsi = indicators.get("RSI", {}).get("value", 50)
    macd = indicators.get("MACD", {})
    ema = indicators.get("EMA", {})
    adx = indicators.get("ADX", {})
    bb = indicators.get("BB", {})
    rec = indicators.get("recommendation", "NEUTRAL")
    conf = indicators.get("confidence", 0)

    user = f"""Pair: {pair} | Timeframe: {timeframe} | Price: {current_price}

INDIKATOR TEKNIKAL:
- RSI(14): {rsi:.2f} ({'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'})
- MACD: {format_dict(macd)}
- EMA: {format_dict(ema)}
- ADX: {format_dict(adx)}
- Bollinger Bands: {format_dict(bb)}
- System Rec: {rec} | Confidence: {conf}%

Output JSON (field TEPAT, TIDAK ada teks lain):
{{
  "signal": "BUY" atau "SELL" atau "NEUTRAL",
  "order_type": "BUY NOW" atau "SELL NOW" atau "BUY LIMIT" atau "SELL LIMIT" atau "BUY STOP" atau "SELL STOP" atau "WAIT",
  "probability": <int 0-100>,
  "grade": "A+" atau "A" atau "B" atau "C",
  "confidence": <int 0-100>,
  "entry": <float harga entry>,
  "sl": <float stop loss>,
  "tp1": <float TP pertama RR 1:1>,
  "tp2": <float TP kedua RR 1:2>,
  "tp3": <float TP ketiga RR 1:3>,
  "rr": "<string misal '1:2.5'>",
  "lot_suggestion": <float>,
  "style": "SCALPING" atau "INTRADAY" atau "SWING",
  "session": "Asia" atau "London" atau "NewYork" atau "London-NY Overlap",
  "trigger": "<1 kalimat: apa yang men-trigger sinyal, misal 'RSI divergence + break OB zone'>",
  "reasoning": "<2-3 kalimat analisa market struktur dan validitas entry>",
  "trading_plan": "<2-3 kalimat rencana trade: kapan entry, exit, lot management>",
  "key_levels": {{"support": <float>, "resistance": <float>}},
  "invalidation": "<1 kalimat kondisi yang membatalkan sinyal>"
}}"""

    ai_text = await ask_kimi(system, user, max_tokens=900)
    result = _parse_json(ai_text)

    active_model = "kimi-2.5" if (KIMI_API_KEY and not KIMI_API_KEY.startswith("sk-REPLACE")) else "deepseek"

    if result and result.get("signal") in ("BUY", "SELL", "NEUTRAL"):
        result["model"] = active_model
        result["pair"] = pair
        result["timeframe"] = timeframe
        result["current_price"] = current_price
        return result

    # Structured fallback
    return {
        "signal": rec if rec in ("BUY", "SELL") else "NEUTRAL",
        "order_type": "WAIT",
        "probability": conf // 2,
        "grade": "C",
        "confidence": conf,
        "entry": round(current_price, 5),
        "sl": None, "tp1": None, "tp2": None, "tp3": None,
        "rr": "N/A",
        "lot_suggestion": 0.01,
        "style": "INTRADAY",
        "session": "London",
        "trigger": "Konfluensi indikator belum cukup kuat untuk sinyal valid",
        "reasoning": ai_text[:300] if len(ai_text) > 10 else "AI sedang menganalisa data teknikal...",
        "trading_plan": "Tunggu konfirmasi tambahan sebelum entry.",
        "key_levels": {"support": None, "resistance": None},
        "invalidation": "Break structure berlawanan arah sinyal",
        "model": active_model,
        "pair": pair,
        "timeframe": timeframe,
        "current_price": current_price,
    }


async def _analyze_pair_for_scanner_kimi_legacy(
    pair: str, timeframe: str, indicators: dict, current_price: float
) -> dict:
    """
    Legacy Kimi scanner — disabled/renamed to avoid overriding backward-compat wrapper above.
    """
    system = (
        "Kamu adalah AI Scanner GAS Strategy AI. "
        "Analisa pair dan hasilkan sinyal dalam JSON valid saja. "
        "Fokus: sinyal berkualitas dengan entry/SL/TP presisi."
    )

    rsi = indicators.get("RSI", {}).get("value", 50)
    rec = indicators.get("recommendation", "NEUTRAL")
    conf = indicators.get("confidence", 0)
    macd_sig = indicators.get("MACD", {}).get("signal", "neutral")
    ema_sig = indicators.get("EMA", {}).get("signal", "neutral")
    adx_str = indicators.get("ADX", {}).get("strength", "weak")

    user = f"""Pair: {pair} | TF: {timeframe} | Price: {current_price}
RSI: {rsi:.1f} | MACD: {macd_sig} | EMA: {ema_sig} | ADX: {adx_str} | System: {rec} ({conf}%)

JSON saja (tidak ada teks lain):
{{
  "signal": "BUY" atau "SELL" atau "NEUTRAL",
  "order_type": "BUY NOW" atau "SELL NOW" atau "BUY LIMIT" atau "SELL LIMIT" atau "WAIT",
  "probability": <int 0-100>,
  "confidence": <int 0-100>,
  "grade": "SS" atau "S" atau "A+" atau "A" atau "B" atau "C",
  "stars": <int 1-5>,
  "entry": <float>,
  "sl": <float>,
  "tp1": <float>,
  "tp2": <float>,
  "tp3": <float>,
  "rr": "<string>",
  "trigger": "<1 kalimat singkat>",
  "reasoning": "<1 kalimat>"
}}"""

    ai_text = await ask_kimi(system, user, max_tokens=450)
    result = _parse_json(ai_text)

    active_model = "kimi-2.5" if (KIMI_API_KEY and not KIMI_API_KEY.startswith("sk-REPLACE")) else "deepseek"

    if result and result.get("signal") in ("BUY", "SELL", "NEUTRAL"):
        result.update({"pair": pair, "price": current_price, "timeframe": timeframe, "model": active_model})
        return result

    return {
        "pair": pair, "price": current_price, "timeframe": timeframe,
        "signal": rec if rec in ("BUY", "SELL") else "NEUTRAL",
        "order_type": "WAIT", "probability": 0, "confidence": conf,
        "grade": "C", "entry": current_price,
        "sl": None, "tp1": None, "tp2": None, "tp3": None,
        "rr": "N/A",
        "trigger": "Data teknikal belum cukup konfluent",
        "reasoning": "Tunggu konfirmasi lebih lanjut",
        "model": active_model,
    }


# ── General Analysis — DeepSeek / OpenRouter ─────────────────────────────────

async def analyze_technical(pair: str, timeframe: str, indicators: dict, current_price: float) -> str:
    system = (
        "Kamu adalah AI trading analyst ahli. Berikan analisis teknikal singkat, "
        "akurat, dan actionable dalam bahasa Indonesia."
    )
    user = (
        f"Pair: {pair} | TF: {timeframe} | Price: {current_price}\n"
        f"Indikator:\n{format_dict(indicators)}\n\n"
        "Berikan: 1) Kondisi market, 2) Setup terdeteksi, 3) Rekomendasi. Max 3 kalimat."
    )
    result = await ask_ai(system, user, max_tokens=300)
    if "[AI Error:" in result or "[Model Error:" in result or "[Kimi Error:" in result:
        return _build_technical_text(pair, timeframe, indicators, current_price)
    return result


async def analyze_sentiment(fear_greed: dict, cot_gold: dict, cot_dxy: dict, pair: str) -> str:
    system = "Kamu adalah AI market sentiment analyst. Analisis sentiment dan berikan kesimpulan actionable dalam bahasa Indonesia."
    user = (
        f"Pair: {pair}\nFear & Greed: {fear_greed}\n"
        f"COT Gold: {format_dict(cot_gold)}\nCOT DXY: {format_dict(cot_dxy)}\n\n"
        "Berikan: 1) Sentiment keseluruhan, 2) Posisi smart money, 3) Sinyal. Max 3 kalimat."
    )
    return await ask_ai(system, user, max_tokens=300)


async def analyze_fundamental(macro_data: dict, pair: str) -> str:
    system = "Kamu adalah AI macro analyst. Analisis fundamental dan dampaknya pada pair dalam bahasa Indonesia."
    user = (
        f"Pair: {pair}\nMakro: {format_dict(macro_data)}\n\n"
        "Berikan: 1) Bias fundamental, 2) Faktor utama, 3) Rekomendasi. Max 4 kalimat."
    )
    return await ask_ai(system, user, max_tokens=400)


async def analyze_hybrid(ta_score: int, fa_score: int, sentiment_score: int,
                          indicators: dict, pair: str, current_price: float,
                          dxy_data: dict = None) -> str:
    system = (
        "Kamu adalah AI analyst confluence. Gabungkan TA+FA+Sentiment+DXY Correlation "
        "dan berikan keputusan final dalam bahasa Indonesia. "
        "DXY rule: DXY↑=XAU↓ (SELL), DXY↓=XAU↑ (BUY). Ini filter wajib untuk XAUUSD."
    )
    dxy_score = (dxy_data or {}).get("score", 50)
    dxy_overall = (dxy_data or {}).get("overall", "NEUTRAL")
    corr_signal = (dxy_data or {}).get("correlation", "NEUTRAL")
    scores = [ta_score, fa_score, sentiment_score, dxy_score]
    confluence = sum(scores) // len(scores)
    dxy_line = f"DXY: {dxy_overall} → Correlation: {corr_signal} (score {dxy_score}/100)\n" if dxy_data else ""
    user = (
        f"Pair: {pair} | Price: {current_price}\n"
        f"TA: {ta_score}/100 | FA: {fa_score}/100 | Sentiment: {sentiment_score}/100 | "
        f"DXY: {dxy_score}/100 | Confluence: {confluence}/100\n"
        f"{dxy_line}"
        f"Technical: {format_dict(indicators)}\n\n"
        "Keputusan BUY/SELL/NEUTRAL dengan reasoning termasuk DXY filter. Max 4 kalimat."
    )
    return await ask_ai(system, user, max_tokens=350)


async def analyze_briefing(macro_data: dict, calendar_events: list,
                            fear_greed: dict, briefing_type: str, mtf_context: dict = None) -> dict:
    """Returns structured briefing dict with headline, market_bias, pairs_outlook, DXY analysis, etc."""
    from datetime import datetime, timedelta, timezone
    wib = timezone(timedelta(hours=7))
    now_wib = datetime.now(wib)

    # Format events for prompt
    events_text = ""
    high_impact_events = []
    for ev in calendar_events[:8]:
        if isinstance(ev, dict):
            impact = str(ev.get("impact", "")).upper()
            events_text += f"- {ev.get('time','')} | {ev.get('currency','')} | {ev.get('event','')} | Impact: {ev.get('impact','?')} | Forecast: {ev.get('forecast','?')} | Prev: {ev.get('previous','?')}\n"
            if "HIGH" in impact:
                high_impact_events.append(ev.get("event", ""))

    type_label = "HARIAN" if briefing_type == "daily" else "MINGGUAN"

    # Build DXY + MTF context for briefing
    dxy_section = ""
    if mtf_context and isinstance(mtf_context, dict):
        xau_mtf = mtf_context.get("xau_mtf", {})
        xau_overall = mtf_context.get("xau_overall", "NEUTRAL")
        dxy_overall = mtf_context.get("dxy_overall", "NEUTRAL")
        corr_signal = mtf_context.get("correlation_signal", "NEUTRAL")
        dxy_avail = mtf_context.get("dxy_available", False)
        mtf_lines = " | ".join(f"{tf}: {tr}" for tf, tr in xau_mtf.items()) if xau_mtf else "no data"
        high_impact_str = ", ".join(high_impact_events[:3]) if high_impact_events else "Tidak ada"
        dxy_section = (
            f"\nXAU MULTI-TF ANALYSIS (Intraday: H4/H1/M15/M5):\n"
            f"- XAU Trend per TF: {mtf_lines}\n"
            f"- XAU Overall Bias: {xau_overall}\n"
            f"\nDXY CORRELATION (DXY↑=XAU↓, DXY↓=XAU↑):\n"
            f"- DXY Trend: {dxy_overall}{'  (data tersedia)' if dxy_avail else ' (DXY tidak tersedia di broker — gunakan logika umum)'}\n"
            f"- Konfluensi Signal: {corr_signal}\n"
            f"\nHIGH-IMPACT NEWS FILTER:\n"
            f"- Event HIGH: {high_impact_str}\n"
            f"- Trading Advice: {'HINDARI trade 30 menit sebelum/sesudah HIGH-impact event' if high_impact_events else 'Aman — tidak ada HIGH-impact event hari ini'}\n"
        )

    system = (
        "Kamu adalah AI Market Briefer profesional GAS Strategy AI. "
        "Selalu response dalam JSON valid. Bahasa Indonesia. "
        "Gunakan metodologi ICT/SMC: DXY inverse correlation untuk XAUUSD. "
        "Filter high-impact news sebagai risk management."
    )
    user = (
        f"Buat {type_label} market briefing untuk trader. Tanggal: {now_wib.strftime('%A, %d %B %Y %H:%M WIB')}\n"
        f"Fear & Greed Index: {fear_greed.get('index','N/A')} ({fear_greed.get('label','N/A')})\n"
        f"Data Makro: GDP={macro_data.get('gdp','N/A')}, Inflation={macro_data.get('inflation','N/A')}, Unemployment={macro_data.get('unemployment','N/A')}\n"
        f"Economic Calendar:\n{events_text or 'Tidak ada event besar hari ini.'}"
        f"{dxy_section}\n"
        "Return JSON dengan format TEPAT:\n"
        '{"headline": "judul singkat menarik max 10 kata",'
        '"market_bias": "bullish|bearish|neutral",'
        '"macro_summary": "ringkasan kondisi makro 2-3 kalimat",'
        '"smart_money_view": "analisa smart money / institutional view 2 kalimat",'
        '"trading_advice": "saran konkret untuk trader retail 2-3 kalimat",'
        '"xau_plan": {"bias": "bullish|bearish|neutral", "dxy_filter": "DXY trend dan implikasinya", "plan_a": "setup entry jika trending", "plan_b": "setup entry dari key level / reversal", "key_levels": "level penting hari ini", "high_impact_warning": "event yang perlu diwaspadai"},'
        '"pairs_outlook": [{"pair": "XAUUSD", "bias": "bullish|bearish|neutral", "note": "catatan singkat"},'
        '{"pair": "EURUSD", "bias": "...", "note": "..."},'
        '{"pair": "GBPUSD", "bias": "...", "note": "..."},'
        '{"pair": "USDJPY", "bias": "...", "note": "..."}],'
        '"key_events": [{"time": "waktu", "event": "nama event", "impact": "HIGH|MEDIUM|LOW", "forecast": "?", "prev": "?"}]}\n'
        "Pastikan key_events berisi max 5 event paling penting. xau_plan WAJIB diisi."
    )
    raw = await ask_ai(system, user, max_tokens=800)

    # Parse JSON from response
    import json, re
    try:
        # Extract JSON from markdown code blocks if present
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group(1))
        else:
            # Try direct parse
            parsed = json.loads(raw)
        return parsed
    except Exception:
        # Fallback: return structured dict with ai text as macro_summary
        return {
            "headline": f"Market {type_label} Update — {now_wib.strftime('%d %b %Y')}",
            "market_bias": "neutral",
            "macro_summary": raw[:400] if raw else "Briefing tidak tersedia saat ini.",
            "smart_money_view": "Smart money sedang akumulasi di zona demand utama.",
            "trading_advice": "Tunggu konfirmasi struktur sebelum entry. Kelola risiko dengan ketat.",
            "pairs_outlook": [
                {"pair": "XAUUSD", "bias": "neutral", "note": "Perhatikan support/resistance kunci"},
                {"pair": "EURUSD", "bias": "neutral", "note": "Ikuti DXY untuk konfirmasi arah"},
                {"pair": "GBPUSD", "bias": "neutral", "note": "Waspada volatilitas data ekonomi"},
                {"pair": "USDJPY", "bias": "neutral", "note": "BOJ policy tetap perlu dipantau"},
            ],
            "key_events": calendar_events[:5],
        }


async def analyze_psychology(emotion: str, risks: list, recent_pnl: str) -> str:
    system = "Kamu adalah AI psychology coach trader. Berikan feedback mindset empatik tapi tegas dalam bahasa Indonesia."
    user = (
        f"Emosi: {emotion}\nRisiko: {', '.join(risks) if risks else 'tidak ada'}\n"
        f"PnL terkini: {recent_pnl or 'tidak diinfokan'}\n\n"
        "Berikan: 1) Penilaian psikologis, 2) Peringatan, 3) Saran konkret. Max 3 kalimat."
    )
    return await ask_ai(system, user, max_tokens=300)


async def analyze_morning_briefing(
    fear_greed: dict, cot_gold: dict, cot_dxy: dict, macro: dict,
    calendar_events: list, vip_data: dict, dxy_data: dict, other_pairs: dict,
    account_info: Optional[dict] = None
) -> str:
    system = (
        "Kamu adalah AI Lead Strategist GAS Strategy AI. Buat Morning Briefing sangat detail, "
        "akurat, profesional untuk trader institusi. Bahasa Indonesia, format Markdown."
    )
    vip_text = "".join(
        f"\n--- {pair} ---\n" + "".join(f"{tf}:\n{d.get('csv','')}\n" for tf, d in tfs.items())
        for pair, tfs in vip_data.items()
    )
    dxy_text = "\n--- DXY ---\n" + "".join(f"{tf}:\n{csv}\n" for tf, csv in dxy_data.items())
    cal_text = "\n".join(
        f"  {ev.get('time','')} | {ev.get('currency','')} | {ev['event']} | {ev.get('impact','?')}"
        for ev in calendar_events[:10] if isinstance(ev, dict)
    )
    user = f"""DATA:\n💰 Equity: ${account_info.get('equity',0) if account_info else 'N/A'}
📊 Fear&Greed: {fear_greed.get('index')} ({fear_greed.get('label')})
COT Gold: {format_dict(cot_gold.get('non_commercial',{}))} | COT DXY: {cot_dxy.get('bias')}
Calendar:\n{cal_text}\nVIP:\n{vip_text}\nDXY:\n{dxy_text}

Buat Morning Briefing 11 section:
1.Macro Bias 2.Market Regime 3.Key Levels H4/H1 4.Liquidity Map 5.FVG&OB
6.Signal BUY/SELL/WAIT 7.Entry/SL/TP 8.Trading Window 9.News Filter
10.Daily Battle Plan 11.Psychology Reminder"""
    return await ask_ai(system, user, max_tokens=1500)


async def analyze_smc(symbol: str, timeframe: str, smc_result: dict) -> str:
    system = (
        "Kamu adalah AI SMC analyst profesional. Interpretasikan analisis SMC, "
        "berikan panduan trading konkret ICT/SMC dalam bahasa Indonesia. Singkat dan actionable."
    )
    ms = smc_result.get("market_structure", {})
    zones = smc_result.get("zones", {})
    signal = smc_result.get("signal", {})
    score = smc_result.get("confluence_score", 0)
    liq = smc_result.get("liquidity", {})
    entry = smc_result.get("entry", {})
    tc = smc_result.get("time_context", {})
    user = f"""Pair: {symbol} | TF: {timeframe} | Score: {score}/100
Signal: {signal.get('action')} | Entry: {signal.get('entry_price')} | SL: {signal.get('stop_loss')} | TP: {signal.get('take_profit')} | RR: {signal.get('rr')}
Bias: {ms.get('bias')} | Structure: {ms.get('structure_type')}
OB: {[f"{ob['type']} H:{ob['high']} L:{ob['low']}" for ob in zones.get('order_blocks',[])]}
FVG: {[f"{f['type']} {f['bottom']}–{f['top']}" for f in zones.get('fvgs',[])]}
Pools: {[f"{p['type']}@{p['level']}" for p in liq.get('pools',[])[:3]]}
Session: {tc.get('session')} | AMD: {tc.get('amd_phase')}

Analisis: 1)Struktur 2)Zona Institusional 3)Likuiditas 4)Entry Setup 5)Keputusan Final. Max 8 kalimat."""
    return await ask_ai(system, user, max_tokens=600)


async def analyze_scanner(pairs_results: list) -> str:
    system = "Kamu adalah AI scanner analyst. Analisis hasil scan multi-pair, rekomendasi top pair dalam bahasa Indonesia."
    user = f"Hasil Scanner:\n{format_list(pairs_results)}\n\nTop 3 pair terbaik + reasoning. Max 3 kalimat."
    return await ask_ai(system, user, max_tokens=300)


async def analyze_correlation(matrix: dict, base_pair: str, live_prices: dict) -> str:
    system = "Kamu adalah AI correlation analyst. Interpretasikan korelasi dan berikan insight trading dalam bahasa Indonesia."
    lines = [f"{p} vs {p2}: {v:+.3f}" for p, corrs in matrix.items() for p2, v in corrs.items() if p != p2]
    user = (
        f"Base: {base_pair}\nHarga: {format_dict(live_prices)}\nKorelasi:\n" +
        "\n".join(lines) + "\n\n1)Korelasi utama 2)Pair berlawanan 3)Strategi. Max 4 kalimat."
    )
    return await ask_ai(system, user, max_tokens=350)


async def analyze_backtest(pair: str, timeframe: str, stats: dict) -> str:
    system = "Kamu adalah AI quant analyst. Evaluasi backtesting dan beri rekomendasi strategi dalam bahasa Indonesia."
    user = f"Pair: {pair} | TF: {timeframe}\nStats:\n{format_dict(stats)}\n\n1)Evaluasi 2)Kelayakan 3)Perbaikan. Max 4 kalimat."
    return await ask_ai(system, user, max_tokens=400)


async def analyze_journal(journal_data: dict) -> str:
    system = "Kamu adalah AI trading coach analisa jurnal. Identifikasi pola dan berikan coaching dalam bahasa Indonesia."
    account = journal_data.get("account") or {}
    positions = journal_data.get("open_positions", [])
    user = (
        f"Akun: Balance ${account.get('balance','N/A')} | Equity ${account.get('equity','N/A')}\n"
        f"Floating PnL: ${account.get('floating_pnl',0)} | Posisi: {len(positions)}\n"
        f"Detail: {format_list(positions, 5)}\n\n1)Kondisi portofolio 2)Posisi kritis 3)Saran. Max 4 kalimat."
    )
    return await ask_ai(system, user, max_tokens=400)


async def analyze_mentor(pair: str, timeframe: str, indicators: dict,
                          current_price: float, account: dict, question: str) -> str:
    system = (
        "Kamu adalah AI Mentor Trading Senior 15+ tahun forex dan gold. "
        "Review setup layaknya mentor profesional — jujur, tegas, actionable. Bahasa Indonesia."
    )
    acc = (f"\nAkun: ${account.get('balance','N/A')} | Posisi: {account.get('positions_count',0)}" if account else "")
    q = f"\nPertanyaan: {question}" if question else ""
    user = (
        f"Pair: {pair} | TF: {timeframe} | Price: {current_price}{acc}{q}\n"
        f"Technical:\n{format_dict(indicators)}\n\n"
        "Mentor: 1)Kondisi chart 2)Validitas setup 3)Entry/SL/TP presisi jika valid 4)Warning. Max 5 kalimat."
    )
    return await ask_ai(system, user, max_tokens=500)


# ── Helpers ───────────────────────────────────────────────────────────────────

def format_dict(d: dict, depth: int = 0) -> str:
    if not d or not isinstance(d, dict):
        return str(d)
    lines = []
    for k, v in d.items():
        if isinstance(v, dict):
            lines.append(f"{k}: {format_dict(v, depth+1)}")
        elif isinstance(v, float):
            lines.append(f"{k}: {v:.4f}")
        else:
            lines.append(f"{k}: {v}")
    return " | ".join(lines)


def format_list(lst: list, limit: int = 5) -> str:
    if not lst:
        return "kosong"
    return "; ".join(str(item) for item in lst[:limit])
