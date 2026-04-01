"""
GAS Bot — Premium MarkdownV2 Formatter
Output: bold headers, italic reasoning, hyperlinks, probability bars,
        box-art entry/SL/TP layout, emoji, clean separators.
"""
import re

SITE_URL = "https://www.gasstrategyai.xyz"
SEP = "━━━━━━━━━━━━━━━━━━━━━━━"


# ── Core escape ────────────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    """Escape all MarkdownV2 reserved characters."""
    special = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(r'([' + re.escape(special) + r'])', r'\\\1', str(text))


# ── Visual helpers ─────────────────────────────────────────────────────────────

def _prob_bar(prob) -> str:
    try:
        n = int(float(prob))
    except Exception:
        return ""
    filled = max(0, min(10, round(n / 10)))
    bar = "█" * filled + "░" * (10 - filled)
    return f"`{bar}` *{_esc(str(n))}%*"


def _stars(n) -> str:
    try:
        n = max(1, min(5, int(n)))
    except Exception:
        n = 2
    return "⭐" * n + "☆" * (5 - n)


def _grade_header(grade: str) -> str:
    g = grade.upper()
    return {
        "SS": "🔥🔥 *SS — SUPREME SIGNAL* 🔥🔥",
        "S":  "⚡⚡ *S — STRONG SIGNAL* ⚡⚡",
        "A+": "💎 *A\\+ — PRIME SIGNAL*",
        "A":  "✅ *A — VALID SIGNAL*",
        "B":  "⚠️ *B — WATCH \\& WAIT*",
        "C":  "❌ *C — SKIP / NEUTRAL*",
    }.get(g, f"📊 *{_esc(grade)} — SIGNAL*")


def _dir_line(direction: str, bias: str) -> str:
    d = str(direction).upper()
    if "BUY" in d or "LONG" in d:
        emoji, label = "📈", "BUY"
    elif "SELL" in d or "SHORT" in d:
        emoji, label = "📉", "SELL"
    else:
        emoji, label = "⏸", "WAIT"
    return f"{emoji} *{label}*  ·  Bias: _{_esc(str(bias))}_"


def _price(val) -> str:
    if val is None or str(val) in ("None", "—", "", "null", "0"):
        return "—"
    return str(val)


def _session_line(session: str) -> str:
    if not session:
        return ""
    parts = [p.strip() for p in re.split(r'[/,|]', session) if p.strip()]
    labeled = []
    for p in parts:
        pu = p.upper()
        if "LONDON" in pu or "LDN" in pu:
            labeled.append("🇬🇧 London")
        elif "NEW YORK" in pu or "NY" in pu:
            labeled.append("🇺🇸 New York")
        elif "ASIA" in pu or "TOKYO" in pu:
            labeled.append("🇯🇵 Tokyo")
        elif "SYDNEY" in pu:
            labeled.append("🇦🇺 Sydney")
        elif "OVERLAP" in pu:
            labeled.append("🔀 Overlap")
        else:
            labeled.append(_esc(p))
    return " / ".join(labeled)


# ── Signal formatter ───────────────────────────────────────────────────────────

def format_signal_md(result: dict, pair: str, style: str) -> str:
    """Premium MarkdownV2 signal card with box-art layout."""
    grade     = result.get("grade", "B")
    stars     = result.get("stars", 2)
    prob      = result.get("probability", result.get("confidence", 0))
    direction = result.get("signal", result.get("direction", "WAIT"))
    bias      = result.get("bias", "Neutral")
    entry     = result.get("entry", result.get("entry_zone"))
    sl        = result.get("stop_loss", result.get("sl"))
    tp1       = result.get("tp1", result.get("take_profit_1"))
    tp2       = result.get("tp2", result.get("take_profit_2"))
    tp3       = result.get("tp3", result.get("take_profit_3"))
    rr        = result.get("rr", result.get("risk_reward", "—"))
    summary   = result.get("summary", result.get("reasoning", result.get("narrative", "")))
    session   = result.get("session", "")
    credits   = result.get("credits_remaining", "?")
    model     = result.get("model", "")

    style_labels = {
        "scalping": "⚡ Scalping",
        "intraday": "🌅 Day Trade",
        "swing":    "🌊 Swing",
        "position": "🏔 Position",
    }
    style_label = _esc(style_labels.get(style.lower(), style.title()))

    lines = [
        SEP,
        _grade_header(grade),
        SEP,
        "",
        f"📌 *{_esc(pair.upper())}*  \\|  {style_label}  \\|  {_stars(stars)}",
        f"📊 {_prob_bar(prob)}",
        "",
        _dir_line(direction, bias),
        "",
    ]

    # Price box using code block (no escaping needed inside ```)
    e = _price(entry)
    s = _price(sl)
    t1 = _price(tp1)
    t2 = _price(tp2)
    t3 = _price(tp3)
    lines += [
        "```",
        f"┌─────────────────────────",
        f"│ 💰 Entry   {e:<12}",
        f"│ 🛡  SL      {s:<12}",
        f"│ 🎯 TP 1    {t1:<12}",
        f"│ 🎯 TP 2    {t2:<12}",
        f"└ 🎯 TP 3    {t3:<12}",
        "```",
        "",
        f"⚖️ R:R *{_esc(str(rr))}*",
    ]

    sess = _session_line(session)
    if sess:
        lines.append(f"🕐 Sesi: {sess}")

    # AI reasoning in italic
    if summary and str(summary).strip():
        trimmed = str(summary).strip()[:450]
        if len(str(summary).strip()) > 450:
            trimmed += "…"
        lines += [
            "",
            "📝 *Analisis AI:*",
            f"_{_esc(trimmed)}_",
        ]

    if model:
        lines.append(f"🤖 _Model: {_esc(str(model))}_")

    lines += [
        "",
        SEP,
        f"💳 Credits tersisa: *{_esc(str(credits))}*",
        f"⚡ _Powered by_ [Golden AI Strategy]({SITE_URL})",
    ]

    return "\n".join(lines)


# ── Analysis formatter (deep technical MTF + calendar + correlation) ──────────

def format_analysis_md(result: dict, pair: str, style: str) -> str:
    """MarkdownV2 card for Analisa flow — MTF technical + calendar + correlation."""
    grade     = result.get("grade", "B")
    stars     = result.get("stars", 3)
    prob      = result.get("probability", result.get("confidence", 0))
    direction = result.get("signal", result.get("direction", "NEUTRAL"))
    bias      = result.get("bias", "Neutral")
    entry     = result.get("entry", result.get("entry_zone"))
    sl        = result.get("stop_loss", result.get("sl"))
    tp1       = result.get("tp1")
    tp2       = result.get("tp2")
    tp3       = result.get("tp3")
    rr        = result.get("rr", result.get("risk_reward", "—"))
    summary   = result.get("summary", result.get("result", {}).get("summary", ""))
    session   = result.get("session", "")
    credits   = result.get("credits_remaining", "?")
    model     = result.get("model", "")
    tf_mtx    = result.get("timeframe_matrix", [])
    cal_ctx   = result.get("calendar_context", "")
    cal_ev    = result.get("calendar_events", [])
    top_corr  = result.get("top_correlation", "")

    style_labels = {
        "scalping": "⚡ Scalping",
        "intraday": "🌅 Day Trade",
        "swing":    "🌊 Swing",
        "position": "🏔 Position",
    }
    style_label = _esc(style_labels.get(style.lower(), style.title()))

    lines = [
        SEP,
        "🔬 *ANALISIS TEKNIKAL MENDALAM*",
        _grade_header(grade),
        SEP,
        "",
        f"📌 *{_esc(pair.upper())}*  \\|  {style_label}  \\|  {_stars(stars)}",
        f"📊 {_prob_bar(prob)}",
        "",
        _dir_line(direction, bias),
        "",
    ]

    # TF matrix badge
    if tf_mtx:
        tf_str = " → ".join(tf_mtx)
        lines.append(f"🗂 TF Matrix: `{tf_str}`")
        lines.append("")

    # Price box
    e  = _price(entry)
    s  = _price(sl)
    t1 = _price(tp1)
    t2 = _price(tp2)
    t3 = _price(tp3)
    lines += [
        "```",
        f"┌─────────────────────────",
        f"│ 💰 Entry   {e:<12}",
        f"│ 🛡  SL      {s:<12}",
        f"│ 🎯 TP 1    {t1:<12}",
        f"│ 🎯 TP 2    {t2:<12}",
        f"└ 🎯 TP 3    {t3:<12}",
        "```",
        "",
        f"⚖️ R:R *{_esc(str(rr))}*",
    ]

    sess = _session_line(session)
    if sess:
        lines.append(f"🕐 Sesi: {sess}")

    # Calendar context
    if cal_ctx:
        lines += ["", f"📅 *Kalender:* _{_esc(cal_ctx)}_"]
        for ev in cal_ev[:2]:
            lines.append(f"  • _{_esc(ev)}_")

    # Top correlation
    if top_corr:
        lines += ["", f"🔗 *Korelasi Tertinggi:* `{_esc(top_corr)}`"]

    # AI reasoning
    if summary and str(summary).strip():
        trimmed = str(summary).strip()[:450]
        if len(str(summary).strip()) > 450:
            trimmed += "…"
        lines += [
            "",
            "📝 *Analisis AI:*",
            f"_{_esc(trimmed)}_",
        ]

    if model:
        lines.append(f"🤖 _Model: {_esc(str(model))}_")

    lines += [
        "",
        SEP,
        f"💳 Credits tersisa: *{_esc(str(credits))}*",
        f"⚡ _Powered by_ [Golden AI Strategy]({SITE_URL})",
    ]
    return "\n".join(lines)


# ── Analyst formatter (full research: hybrid + fundamental + trend + phase) ───

def format_analyst_md(result: dict, pair: str, style: str) -> str:
    """MarkdownV2 card for Analyst flow — full research report."""
    grade       = result.get("grade", "A")
    stars       = result.get("stars", 4)
    prob        = result.get("probability", result.get("confidence", 0))
    direction   = result.get("signal", result.get("direction", "NEUTRAL"))
    bias        = result.get("bias", "Neutral")
    entry       = result.get("entry", result.get("entry_zone"))
    sl          = result.get("stop_loss", result.get("sl"))
    tp1         = result.get("tp1")
    tp2         = result.get("tp2")
    tp3         = result.get("tp3")
    rr          = result.get("rr", result.get("risk_reward", "—"))
    summary     = result.get("summary", result.get("result", {}).get("summary", ""))
    ai_reason   = result.get("ai_reasoning", "")
    session     = result.get("session", "")
    credits     = result.get("credits_remaining", "?")
    model       = result.get("model", "")
    fundamental = result.get("fundamental", "")
    trend_dir   = result.get("trend_direction", "")
    trend_str   = result.get("trend_strength", "")
    mkt_phase   = result.get("market_phase", "")
    phase_conf  = result.get("phase_confidence", "")

    style_labels = {
        "scalping": "⚡ Scalping",
        "intraday": "🌅 Day Trade",
        "swing":    "🌊 Swing",
        "position": "🏔 Position",
    }
    style_label = _esc(style_labels.get(style.lower(), style.title()))

    lines = [
        SEP,
        "🏆 *FULL AI ANALYST REPORT*",
        _grade_header(grade),
        SEP,
        "",
        f"📌 *{_esc(pair.upper())}*  \\|  {style_label}  \\|  {_stars(stars)}",
        f"📊 {_prob_bar(prob)}",
        "",
        _dir_line(direction, bias),
        "",
    ]

    # Market context box
    ctx_lines = []
    if trend_dir:
        t = f"Trend: {trend_dir}" + (f" ({trend_str})" if trend_str else "")
        ctx_lines.append(t)
    if mkt_phase:
        p = f"Phase: {mkt_phase}" + (f" ({phase_conf})" if phase_conf else "")
        ctx_lines.append(p)
    if ctx_lines:
        lines += ["```"] + ctx_lines + ["```", ""]

    # Price box
    e  = _price(entry)
    s  = _price(sl)
    t1 = _price(tp1)
    t2 = _price(tp2)
    t3 = _price(tp3)
    lines += [
        "```",
        f"┌─────────────────────────",
        f"│ 💰 Entry   {e:<12}",
        f"│ 🛡  SL      {s:<12}",
        f"│ 🎯 TP 1    {t1:<12}",
        f"│ 🎯 TP 2    {t2:<12}",
        f"└ 🎯 TP 3    {t3:<12}",
        "```",
        "",
        f"⚖️ R:R *{_esc(str(rr))}*",
    ]

    sess = _session_line(session)
    if sess:
        lines.append(f"🕐 Sesi: {sess}")

    # Fundamental macro
    if fundamental and str(fundamental).strip():
        fund_trimmed = str(fundamental).strip()[:300]
        lines += [
            "",
            "🏦 *Fundamental Makro:*",
            f"_{_esc(fund_trimmed)}_",
        ]

    # AI hybrid reasoning (primary narrative)
    narrative = ai_reason or summary
    if narrative and str(narrative).strip():
        trimmed = str(narrative).strip()[:500]
        if len(str(narrative).strip()) > 500:
            trimmed += "…"
        lines += [
            "",
            "🧠 *AI Reasoning:*",
            f"_{_esc(trimmed)}_",
        ]

    if model:
        lines.append(f"🤖 _Model: {_esc(str(model))}_")

    lines += [
        "",
        SEP,
        f"💳 Credits tersisa: *{_esc(str(credits))}*",
        f"⚡ _Powered by_ [Golden AI Strategy]({SITE_URL})",
    ]
    return "\n".join(lines)


# ── Status formatter ───────────────────────────────────────────────────────────

def format_status_md(plan: str, credits: int, xp: int, username: str) -> str:
    plan_badges = {
        "ultra":     "⚡ Ultra",
        "ultimate":  "👑 Ultimate",
        "premium":   "💎 Premium",
        "plus":      "➕ Plus",
        "essential": "🔵 Essential",
        "trial":     "🎁 Trial",
        "free":      "🆓 Free",
    }
    badge = plan_badges.get(plan.lower(), _esc(plan.title()))
    level_emoji = "🥉" if xp < 500 else "🥈" if xp < 2000 else "🥇" if xp < 5000 else "🏆"
    level_name  = "Bronze" if xp < 500 else "Silver" if xp < 2000 else "Gold" if xp < 5000 else "Platinum"

    cr = min(credits, 100)
    cr_filled = min(10, round(cr / 10))
    cr_bar = "█" * cr_filled + "░" * (10 - cr_filled)

    return (
        f"{SEP}\n"
        f"📊 *Status Akun GAS*\n"
        f"{SEP}\n\n"
        f"👤 User: `{_esc(username)}`\n"
        f"🎫 Plan: *{badge}*\n\n"
        f"💳 Credits: *{_esc(str(credits))}*\n"
        f"`{cr_bar}` _{_esc(str(credits))} cr_\n\n"
        f"{level_emoji} Level: *{level_name}*  \\|  XP: *{_esc(str(xp))}*\n\n"
        f"{SEP}\n"
        f"_Topup & upgrade di_ [GAS Dashboard]({SITE_URL}/pricing)"
    )


# ── Error formatter ────────────────────────────────────────────────────────────

_ERROR_MSGS = {
    "not_linked": (
        "🔗 *Akun Belum Terhubung*\n\n"
        "Bot ini terhubung ke akun GAS kamu\\.\n\n"
        "*Cara menghubungkan:*\n"
        f"1\\. Daftar/login di [gasstrategyai\\.xyz]({SITE_URL})\n"
        "2\\. Ketik /link di bot ini\n"
        "3\\. Buka link di browser \\(berlaku 15 menit\\)\n"
        "4\\. Ketik /start → selesai ✅"
    ),
    "no_credits": (
        "💳 *Credits Habis*\n\n"
        "Tidak cukup credits untuk analisis ini\\.\n\n"
        "📦 *Cara topup:*\n"
        f"• [Buka GAS Dashboard]({SITE_URL}/pricing)\n"
        "• Pilih paket credits\n"
        "• Bayar via USDT \\(TRC20 / ERC20 / BEP20\\)"
    ),
    "plan_required": (
        "🔒 *Fitur Terkunci*\n\n"
        "Fitur ini memerlukan plan *Essential* atau lebih tinggi\\.\n\n"
        f"➡️ [Upgrade Plan Sekarang]({SITE_URL}/pricing)"
    ),
    "analysis_failed": (
        "⚠️ *Analisis Gagal*\n\n"
        "_Kemungkinan penyebab:_\n"
        "• AI engine sedang overload\n"
        "• Pair tidak tersedia saat ini\n"
        "• Koneksi timeout\n\n"
        "Coba lagi dalam beberapa detik\\."
    ),
    "timeout": (
        "⏳ *Server Sedang Sibuk*\n\n"
        "AI engine membutuhkan waktu lebih dari biasa\\.\n\n"
        "_Coba lagi dalam 30 detik\\._ ☕"
    ),
    "invalid_pair": (
        "❌ *Pair Tidak Valid*\n\n"
        "Pair yang diminta tidak tersedia\\.\n"
        "Pilih dari menu yang tersedia\\."
    ),
}


def format_error_md(code: str, detail: str = "") -> str:
    return _ERROR_MSGS.get(code, f"❌ *Error*\n\n_{_esc(detail or code)}_")


# ── Calendar formatter ─────────────────────────────────────────────────────────

def format_calendar_md(events: list) -> str:
    if not events:
        return (
            f"{SEP}\n"
            f"📅 *Kalender Ekonomi*\n"
            f"{SEP}\n\n"
            "_Tidak ada event high\\-impact hari ini\\._"
        )
    impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    lines = [SEP, "📅 *Kalender Ekonomi — Hari Ini*", SEP, ""]
    for ev in events[:12]:
        time_  = _esc(str(ev.get("time", ev.get("date", "—"))))
        title  = _esc(str(ev.get("title", ev.get("event", "—")))[:50])
        impact = str(ev.get("impact", ev.get("importance", "low"))).lower()
        curr   = _esc(str(ev.get("currency", ev.get("country", ""))))
        ie     = impact_emoji.get(impact, "⚪")
        lines.append(f"{ie} *{time_}*  {curr}  {title}")
    lines += ["", f"_Live: [GAS Dashboard]({SITE_URL})_"]
    return "\n".join(lines)


# ── Session card ───────────────────────────────────────────────────────────────

def format_sessions_md() -> str:
    return (
        f"{SEP}\n"
        f"🌏 *Sesi Trading Global \\(WIB UTC\\+7\\)*\n"
        f"{SEP}\n\n"
        f"🇦🇺 *Sydney*    04:00 – 13:00 WIB\n"
        f"🇯🇵 *Tokyo*     06:00 – 15:00 WIB\n"
        f"🇬🇧 *London*    14:00 – 23:00 WIB\n"
        f"🇺🇸 *New York*  19:00 – 04:00 WIB \\(\\+1\\)\n\n"
        f"🔥 *London\\-NY Overlap*: 19:00–23:00  ← _best liquidity_\n"
        f"🔀 *Asia\\-London Overlap*: 14:00–15:00\n\n"
        f"{SEP}\n"
        f"_Gunakan Kill Zone untuk entry presisi_"
    )
