"""
GAS Telegram Bot — Handlers v5.0
Architecture:
  ReplyKeyboard  → 10-button main nav (always at bottom)
  InlineKeyboard → section detail views & flow steps
  MessageHandler → routes ReplyKeyboard taps by text
  CallbackHandler → routes all inline button taps

Flows:
  📊 Signal  → Market → Style → Output          (3 steps, featured pair)
  🧠 Analisa → Market → Pair → Style → Output   (4 steps)
  👑 Analyst → Market → Pair → Style → Full AI  (4 steps, full power)
  🌍 Market  → (same as Analisa flow)
"""
import asyncio
import hashlib
import json
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters,
)
from telegram.constants import ParseMode

from src.config import settings, BOT_ALLOWED_PLANS, get_plan_cfg
from src.utils.logger import logger
from src.utils.formatter import (
    format_signal_md, format_status_md, format_error_md,
    format_calendar_md, format_sessions_md, _esc, SEP,
)
from src.utils.session import set_state, get_state, update_state, clear_state
from src.services.auth_service import (
    generate_link_code, check_bot_access, get_user_credits,
    get_user_xp, get_booster, is_plan_allowed,
)
from src.services.redis_client import get_redis
from src.services.queue import enqueue, JobType
from src.services import cache as signal_cache
from src.keyboards.market import (
    market_category_keyboard, polymarket_keyboard, pair_keyboard_for_plan,
    CAT_KEYBOARDS, CAT_LABELS, FEATURED_PAIR,
    FOREX_PAIRS, CRYPTO_PAIRS, COMMODITY_PAIRS, INDEX_PAIRS, MEME_PAIRS,
)
from src.keyboards.style import style_keyboard, confirm_analysis_keyboard, STYLE_LABELS
from src.keyboards.main_menu import (
    main_menu_keyboard, main_menu_inline_keyboard,
    news_menu_keyboard, tools_menu_keyboard, journal_menu_keyboard,
    guide_menu_keyboard, support_menu_keyboard, plan_menu_keyboard,
    # backward-compat aliases
    jurnal_menu_keyboard, calc_menu_keyboard,
    mydash_menu_keyboard, academy_menu_keyboard,
)

SITE_URL        = settings.SITE_URL
IDEMPOTENCY_TTL = 10

STYLE_COST = {"scalping": 2, "intraday": 3, "swing": 4, "position": 5}
FREE_COST_OVERRIDE = 1

_PLAN_BADGE = {
    "ultra":     "⚡ Ultra",
    "ultimate":  "👑 Ultimate",
    "premium":   "💎 Premium",
    "plus":      "➕ Plus",
    "essential": "🔵 Essential",
    "trial":     "🎁 Trial",
    "free":      "🆓 Free",
}

_FLOW_LABELS = {
    "signal":   "📊 Signal AI",
    "analysis": "🧠 Analisa AI",
    "analyst":  "👑 Golden Analyst",
}

_FLOW_JOB_TYPE = {
    "signal":   JobType.SIGNAL,
    "analysis": JobType.ANALYSIS,
    "analyst":  JobType.ANALYST,
}

# Bot commands registered at startup
BOT_COMMANDS = [
    BotCommand("start",    "🚀 Mulai bot"),
    BotCommand("menu",     "🧭 Menu utama"),
    BotCommand("signal",   "📊 AI Signal"),
    BotCommand("analysis", "🧠 Analisa AI"),
    BotCommand("analyst",  "👑 Golden Analyst"),
    BotCommand("market",   "🌍 Pilih market"),
    BotCommand("tools",    "🧮 Trading tools"),
    BotCommand("plan",     "💎 Upgrade plan"),
    BotCommand("journal",  "🧾 Trading journal"),
    BotCommand("news",     "📰 Market news"),
    BotCommand("help",     "📘 Panduan"),
    BotCommand("support",  "❓ Support"),
]


# ── Core helpers ───────────────────────────────────────────────────────────────

def _plan_badge(plan: str) -> str:
    return _PLAN_BADGE.get(plan.lower(), plan.title())


def _back_btn(label: str, cb: str) -> InlineKeyboardMarkup:
    """Back button: section back + home button."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=cb),
         InlineKeyboardButton("🏠 Menu", callback_data="m_main_menu")],
    ])


async def _edit(query, text: str, markup=None):
    kw = dict(text=text, parse_mode=ParseMode.MARKDOWN_V2)
    if markup is not None:
        kw["reply_markup"] = markup
    try:
        await query.message.edit_text(**kw)
    except Exception:
        await query.message.reply_text(**kw)


async def _send(update: Update, text: str, markup=None):
    """Send a new message (used in text/command handlers)."""
    kw = dict(text=text, parse_mode=ParseMode.MARKDOWN_V2)
    if markup is not None:
        kw["reply_markup"] = markup
    await update.message.reply_text(**kw)


async def _ensure_access(update_or_user_id) -> tuple:
    """Returns (gas_user_id, plan) or (None, None)."""
    if hasattr(update_or_user_id, 'effective_user'):
        tg_id = update_or_user_id.effective_user.id
    else:
        tg_id = update_or_user_id
    return await check_bot_access(tg_id)


async def _check_idempotency(user_id: int, pair: str, style: str) -> bool:
    key = f"req:{user_id}:{hashlib.md5(f'{pair}{style}{int(time.time()//IDEMPOTENCY_TTL)}'.encode()).hexdigest()}"
    try:
        r = await get_redis()
        return await r.set(key, "1", ex=IDEMPOTENCY_TTL, nx=True) is not None
    except Exception:
        return True


def _welcome_text(plan: str, credits: int, name: str, xp: int = 0, booster: str = "") -> str:
    badge        = _plan_badge(plan)
    level        = "Bronze" if xp < 500 else "Silver" if xp < 2000 else "Gold" if xp < 5000 else "Platinum"
    level_emoji  = "🥉" if xp < 500 else "🥈" if xp < 2000 else "🥇" if xp < 5000 else "🏆"
    boost_line   = f"\n⚡ Booster: *{_esc(booster.title())}*" if booster else ""

    if plan in ("ultimate", "ultra"):
        features = (
            "• ⚡ Signal AI \\(Auto Entry\\)\n"
            "• 🧠 Analisa AI \\(Multi TF\\)\n"
            "• 👑 Golden AI Analyst \\(Full Power\\)\n"
            "• 🔍 Market Scanner \\(15 pairs\\)\n"
            "• 📊 Backtesting Engine"
        )
    elif plan == "premium":
        features = (
            "• ⚡ Signal AI \\(Auto Entry\\)\n"
            "• 🧠 Analisa AI \\(Multi TF\\)\n"
            "• 👑 Golden AI Analyst\n"
            "• 🌅 Market Briefing Harian"
        )
    elif plan == "plus":
        features = (
            "• ⚡ Signal AI \\(Auto Entry\\)\n"
            "• 🧠 Analisa AI \\(Multi TF\\)\n"
            "• 📊 Korelasi & Fundamental"
        )
    else:
        features = (
            "• ⚡ Signal AI \\(Basic\\)\n"
            "• 📊 Analisis Teknikal\n"
            "• 📅 Kalender Ekonomi"
        )

    return (
        f"🚀 *Golden AI Strategy Bot*\n\n"
        f"Halo, *{_esc(name)}* 👋\n\n"
        f"━━━━━━━━━━\n\n"
        f"{badge} Plan: *{badge}*\n"
        f"💳 Credits: *{_esc(str(credits))}*\n"
        f"{level_emoji} Level: *{level}*  \\|  XP: *{_esc(str(xp))}*"
        f"{boost_line}\n\n"
        f"━━━━━━━━━━\n\n"
        f"📊 *AI Trading System Aktif:*\n"
        f"{features}\n\n"
        f"━━━━━━━━━━\n\n"
        f"🔥 Status: *Siap Trading*\n"
        f"⚡ Pilih menu di bawah untuk mulai\n\n"
        f"👇👇👇"
    )


# ── Flow entry helpers ─────────────────────────────────────────────────────────

async def _start_flow(update: Update, user_id: int, flow_type: str, plan: str = "free"):
    """Common entry for Signal / Analisa / Analyst flows."""
    await set_state(user_id, "flow_type", flow_type)
    await set_state(user_id, "plan", plan)
    flow_label = _FLOW_LABELS.get(flow_type, flow_type)
    cfg = get_plan_cfg(plan)
    ai_label = {"basic": "⚙️ Basic AI", "advanced": "🚀 Advanced AI",
                "pro": "💎 Pro AI", "ultra": "⚡ Ultra AI"}.get(cfg["ai_tier"], "AI")
    cache_note = "• No cache \\(always fresh\\)" if cfg["cache_ttl"] == 0 else f"• Cache {cfg['cache_ttl']}s"
    await _send(update,
        f"*{_esc(flow_label)}*\n\n"
        f"{_esc(cfg['label'])}  ·  {ai_label}\n"
        f"{cache_note}\n\n"
        f"Pilih kategori market:",
        market_category_keyboard(flow_type, plan))


# ── Analysis execution ─────────────────────────────────────────────────────────

def _result_keyboard(pair: str, style: str, flow_type: str = "signal") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh",     callback_data=f"exec_{flow_type}_{pair}_{style}"),
         InlineKeyboardButton("📊 Pair Lain",   callback_data=f"nav_market_{flow_type}")],
        [InlineKeyboardButton("🏠 Menu Utama",  callback_data="m_main_menu")],
    ])


async def _run_analysis(query, gas_user_id: str, pair: str, style: str, flow_type: str, plan: str = None):
    """Queue job. Workers deliver result by editing this message."""
    user_id   = query.from_user.id
    pair      = pair.upper()
    style     = style.lower()
    job_type  = _FLOW_JOB_TYPE.get(flow_type, JobType.SIGNAL)

    # Get plan from session if not passed
    if not plan:
        plan = await get_state(user_id, "plan", "free")
    cfg = get_plan_cfg(plan)

    # Gate: check style allowed for plan
    if style not in cfg.get("styles", set()):
        upgrade_to = cfg.get("upgrade_to", "plus")
        await query.answer(f"Style ini memerlukan plan {upgrade_to}. Upgrade dulu!", show_alert=True)
        return

    # Gate: check pair allowed for plan
    limit_pairs = cfg.get("limit_pairs")
    if limit_pairs and pair not in limit_pairs:
        upgrade_to = cfg.get("upgrade_to", "essential")
        await _edit(query,
            f"🔒 *Pair Terkunci*\n\n"
            f"Pair *{_esc(pair)}* memerlukan plan *{_esc(upgrade_to.title())}* atau lebih tinggi\\.\n\n"
            f"Plan kamu: *{_esc(cfg['label'])}*\n\n"
            f"_Upgrade untuk akses semua pairs\\!_",
            InlineKeyboardMarkup([
                [InlineKeyboardButton(f"💎 Upgrade ke {upgrade_to.title()}", url=f"{SITE_URL}/pricing")],
                [InlineKeyboardButton("🔙 Pilih Pair Lain", callback_data=f"nav_market_{flow_type}")],
            ]))
        return

    if not await _check_idempotency(user_id, pair, f"{flow_type}_{style}"):
        await query.message.reply_text(
            "⏳ Analisis sedang berjalan\\. Tunggu sebentar\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    # Cache check (skip for analyst or cache_ttl=0)
    cache_ttl = cfg.get("cache_ttl", 30)
    if flow_type != "analyst" and cache_ttl > 0:
        cached = await signal_cache.get_signal(pair, style)
        if cached:
            cached["credits_remaining"] = await get_user_credits(gas_user_id)
            await query.message.edit_text(
                f"✅ *Sinyal Cache \\({cache_ttl}s\\)*\n\n" + format_signal_md(cached, pair, style),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=_result_keyboard(pair, style, flow_type),
            )
            return

    ai_tier    = cfg.get("ai_tier", "basic")
    flow_label = _esc(_FLOW_LABELS.get(flow_type, flow_type))
    eta        = "10–20" if flow_type == "analyst" else ("5–10" if ai_tier in ("advanced", "pro") else "3–5")

    queued_msg = await query.message.edit_text(
        f"📬 *{flow_label}: {_esc(pair)}\\.\\.\\.*\n\n"
        f"`▓░░░░░░░░░`  0%\n\n"
        f"_Estimasi: {eta} detik_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await enqueue(
        job_type=job_type,
        gas_user_id=gas_user_id,
        tg_user_id=user_id,
        chat_id=queued_msg.chat_id,
        message_id=queued_msg.message_id,
        pair=pair,
        style=style,
        plan=plan,
        ai_tier=ai_tier,
        cache_ttl=cache_ttl,
    )
    logger.info("job_enqueued", flow=flow_type, pair=pair, style=style, ai_tier=ai_tier, plan=plan, user=user_id)


# ── /start ─────────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg  = await update.message.reply_text(
        "⚡ _Menginisialisasi GAS Bot\\.\\.\\._",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await asyncio.sleep(0.5)

    gas_user_id, plan = await check_bot_access(user.id)
    if not gas_user_id:
        await msg.edit_text(
            f"🚀 *Golden AI Strategy Bot*\n\n"
            f"Halo, *{_esc(user.first_name)}* 👋\n\n"
            f"━━━━━━━━━━\n\n"
            f"Bot ini terhubung ke akun GAS kamu\\.\n\n"
            f"*Cara mulai:*\n"
            f"1\\. Daftar di [gasstrategyai\\.xyz]({SITE_URL}/signup)\n"
            f"2\\. Ketik /link → buka link di browser\n"
            f"3\\. Ketik /start lagi → siap\\! ✅",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Daftar Gratis", url=f"{SITE_URL}/signup")],
                [InlineKeyboardButton("🔗 Hubungkan Akun", callback_data="do_link")],
            ]),
        )
        return

    credits = await get_user_credits(gas_user_id)
    xp      = await get_user_xp(gas_user_id)
    booster = await get_booster(gas_user_id)

    # ReplyKeyboardMarkup cannot be attached via edit_text — must send new message
    try:
        await msg.delete()
    except Exception:
        pass
    await update.message.reply_text(
        _welcome_text(plan, credits, user.first_name, xp, booster or ""),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_menu_keyboard(),
    )


# ── /menu ──────────────────────────────────────────────────────────────────────

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gas_user_id, plan = await check_bot_access(update.effective_user.id)
    if not gas_user_id:
        await _send(update, format_error_md("not_linked"))
        return
    credits = await get_user_credits(gas_user_id)
    await _send(update,
        f"🧭 *Menu Utama*\n\n"
        f"🎫 Plan: *{_plan_badge(plan)}*  ·  💳 Credits: *{_esc(str(credits))}*\n\n"
        f"_Pilih menu di keyboard bawah_ 👇",
        main_menu_keyboard())


# ── /signal, /analysis, /analyst ──────────────────────────────────────────────

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gas_user_id, plan = await check_bot_access(update.effective_user.id)
    if not gas_user_id:
        await _send(update, format_error_md("not_linked")); return
    await _start_flow(update, update.effective_user.id, "signal", plan or "free")


async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gas_user_id, plan = await check_bot_access(update.effective_user.id)
    if not gas_user_id:
        await _send(update, format_error_md("not_linked")); return
    cfg = get_plan_cfg(plan or "free")
    if "analysis" not in cfg["flows"]:
        upgrade_to = cfg.get("upgrade_to", "plus")
        await _send(update,
            f"🔒 *Analisa AI*\n\nPlan kamu: *{_esc(cfg['label'])}*\n\n"
            f"Analisa tersedia mulai plan *{_esc(upgrade_to.title())}*\\.",
            InlineKeyboardMarkup([[InlineKeyboardButton(f"💎 Upgrade", url=f"{SITE_URL}/pricing")]])); return
    await _start_flow(update, update.effective_user.id, "analysis", plan or "free")


async def analyst_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gas_user_id, plan = await check_bot_access(update.effective_user.id)
    if not gas_user_id:
        await _send(update, format_error_md("not_linked")); return
    cfg = get_plan_cfg(plan or "free")
    if "analyst" not in cfg["flows"]:
        upgrade_to = cfg.get("upgrade_to", "premium")
        await _send(update,
            f"🔒 *Golden Analyst*\n\nPlan kamu: *{_esc(cfg['label'])}*\n\n"
            f"Analyst tersedia mulai plan *{_esc(upgrade_to.title())}*\\.",
            InlineKeyboardMarkup([[InlineKeyboardButton(f"💎 Upgrade", url=f"{SITE_URL}/pricing")]])); return
    await _start_flow(update, update.effective_user.id, "analyst", plan or "free")


# ── /market ────────────────────────────────────────────────────────────────────

async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gas_user_id, plan = await check_bot_access(update.effective_user.id)
    if not gas_user_id:
        await _send(update, format_error_md("not_linked")); return
    plan = plan or "free"
    await set_state(update.effective_user.id, "flow_type", "analysis")
    await set_state(update.effective_user.id, "plan", plan)
    await _send(update, f"🌍 *Pilih Market*\n\nKategori market untuk analisis:",
        market_category_keyboard("analysis", plan))


# ── /tools ─────────────────────────────────────────────────────────────────────

async def tools_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send(update,
        f"🧮 *Trading Tools*\n\nKalkulator dan tools presisi:",
        tools_menu_keyboard())


# ── /plan ──────────────────────────────────────────────────────────────────────

async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send(update,
        f"💎 *Upgrade Plan GAS*\n\n"
        f"Pilih plan yang sesuai kebutuhan kamu:",
        plan_menu_keyboard())


# ── /journal ───────────────────────────────────────────────────────────────────

async def journal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send(update,
        f"🧾 *Trade Journal*\n\nCatat dan evaluasi setiap trade:",
        journal_menu_keyboard())


# ── /news ──────────────────────────────────────────────────────────────────────

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send(update,
        f"📰 *News & Intelligence*\n\nPilih kategori:",
        news_menu_keyboard())


# ── /help ──────────────────────────────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send(update,
        f"📘 *Panduan GAS Bot*\n\n"
        f"*Commands:*\n"
        f"/signal — 📊 Signal AI cepat\n"
        f"/analysis — 🧠 Analisa detail\n"
        f"/analyst — 👑 Full power AI\n"
        f"/market — 🌍 Market browser\n"
        f"/tools — 🧮 Kalkulator\n"
        f"/news — 📰 Berita & sentimen\n"
        f"/journal — 🧾 Trade journal\n"
        f"/plan — 💎 Upgrade plan\n"
        f"/status — 💳 Cek credits\n\n"
        f"*Flow Analisis:*\n"
        f"Signal → Market → Style → Output\n"
        f"Analisa → Market → Pair → Style → Output\n\n"
        f"_Masalah? Tap ❓ Support_",
        guide_menu_keyboard())


# ── /status ────────────────────────────────────────────────────────────────────

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    gas_user_id, plan = await check_bot_access(user.id)
    if not gas_user_id:
        await _send(update, format_error_md("not_linked"),
            InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Hubungkan", callback_data="do_link")]])); return
    credits  = await get_user_credits(gas_user_id)
    xp       = await get_user_xp(gas_user_id)
    username = user.username or user.first_name
    await _send(update,
        format_status_md(plan, credits, xp, username),
        main_menu_inline_keyboard())


# ── /support ───────────────────────────────────────────────────────────────────

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send(update,
        f"❓ *Support GAS*\n\nTim support siap membantu 24/7:",
        support_menu_keyboard())


# ── /link ──────────────────────────────────────────────────────────────────────

async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user     = update.effective_user
    code     = await generate_link_code(user.id)
    link_url = f"{SITE_URL}/link-tg?code={code}"
    await _send(update,
        f"🔗 *Hubungkan Akun GAS*\n\n"
        f"1\\. Login ke [gasstrategyai\\.xyz]({SITE_URL})\n"
        f"2\\. Buka link ini \\(berlaku *15 menit*\\)\n"
        f"3\\. Klik *Hubungkan*\n"
        f"4\\. Ketik /start ✅",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Buka Link", url=link_url)],
            [InlineKeyboardButton("📝 Daftar Akun", url=f"{SITE_URL}/signup")],
        ]))


# ── ReplyKeyboard text message router ─────────────────────────────────────────

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text    = update.message.text.strip()
    user    = update.effective_user
    logger.info("text_message", user_id=user.id, text=text)
    print(f"[USER CLICK] uid={user.id} text={text!r}")

    # ── 📊 SIGNAL ─────────────────────────────────────────────────────────────
    if text == "📊 Signal":
        gas_user_id, plan = await check_bot_access(user.id)
        if not gas_user_id:
            await _send(update, format_error_md("not_linked")); return
        await _start_flow(update, user.id, "signal", plan or "free")
        return

    # ── 🧠 ANALISA ────────────────────────────────────────────────────────────
    if text == "🧠 Analisa":
        gas_user_id, plan = await check_bot_access(user.id)
        if not gas_user_id:
            await _send(update, format_error_md("not_linked")); return
        cfg = get_plan_cfg(plan or "free")
        if "analysis" not in cfg["flows"]:
            upgrade_to = cfg.get("upgrade_to", "plus")
            await _send(update,
                f"🔒 *Analisa AI*\n\n"
                f"Plan kamu: *{_esc(cfg['label'])}*\n\n"
                f"Fitur Analisa AI tersedia mulai plan *{_esc(upgrade_to.title())}*\\.\n"
                f"Analisa AI memberikan analisis mendalam dengan pair picker\\.",
                InlineKeyboardMarkup([[InlineKeyboardButton(f"💎 Upgrade ke {upgrade_to.title()}", url=f"{SITE_URL}/pricing")]])); return
        await _start_flow(update, user.id, "analysis", plan or "free")
        return

    # ── 👑 ANALYST ────────────────────────────────────────────────────────────
    if text == "👑 Analyst":
        gas_user_id, plan = await check_bot_access(user.id)
        if not gas_user_id:
            await _send(update, format_error_md("not_linked")); return
        cfg = get_plan_cfg(plan or "free")
        if "analyst" not in cfg["flows"]:
            upgrade_to = cfg.get("upgrade_to", "premium")
            await _send(update,
                f"🔒 *Golden AI Analyst*\n\n"
                f"Plan kamu: *{_esc(cfg['label'])}*\n\n"
                f"Golden Analyst tersedia mulai plan *{_esc(upgrade_to.title())}*\\.\n"
                f"Menggunakan AI penuh tanpa cache, analisis terdalam\\.",
                InlineKeyboardMarkup([[InlineKeyboardButton(f"💎 Upgrade ke {upgrade_to.title()}", url=f"{SITE_URL}/pricing")]])); return
        await _start_flow(update, user.id, "analyst", plan or "free")
        return

    # ── 🌍 MARKET ─────────────────────────────────────────────────────────────
    if text == "🌍 Market":
        gas_user_id, plan = await check_bot_access(user.id)
        if not gas_user_id:
            await _send(update, format_error_md("not_linked")); return
        plan = plan or "free"
        await set_state(user.id, "flow_type", "analysis")
        await set_state(user.id, "plan", plan)
        await _send(update,
            f"🌍 *Pilih Market*\n\nKategori market untuk analisis:",
            market_category_keyboard("analysis", plan))
        return

    # ── 📰 NEWS ───────────────────────────────────────────────────────────────
    if text == "📰 News":
        await _send(update,
            f"📰 *News & Intelligence*\n\nPilih kategori:",
            news_menu_keyboard())
        return

    # ── 💎 UPGRADE ────────────────────────────────────────────────────────────
    if text == "💎 Upgrade":
        await _send(update,
            f"💎 *Upgrade Plan GAS*\n\n"
            f"🔵 *Essential* — Rp 29\\.900/bln\n"
            f"  Signal AI, Technical, Session, Calendar\n\n"
            f"➕ *Plus* — Rp 59\\.900/bln\n"
            f"  \\+ Analisa AI, Korelasi, Fundamental\n\n"
            f"💎 *Premium* — Rp 119\\.900/bln\n"
            f"  \\+ Analyst, Briefing, Psychology, Journal\n\n"
            f"👑 *Ultimate* — Rp 199\\.900/bln\n"
            f"  Full AI \\+ Scanner \\+ Backtesting \\+ Mentor\n\n"
            f"_Bayar via USDT TRC20/ERC20/BEP20_",
            plan_menu_keyboard())
        return

    # ── 🧾 JOURNAL ────────────────────────────────────────────────────────────
    if text == "🧾 Journal":
        await _send(update,
            f"🧾 *Trade Journal*\n\nCatat dan evaluasi setiap trade:",
            journal_menu_keyboard())
        return

    # ── 🧮 TOOLS ─────────────────────────────────────────────────────────────
    if text == "🧮 Tools":
        await _send(update,
            f"🧮 *Trading Tools*\n\nKalkulator dan tools presisi:",
            tools_menu_keyboard())
        return

    # ── 📘 GUIDE ─────────────────────────────────────────────────────────────
    if text == "📘 Guide":
        await _send(update,
            f"📘 *Panduan GAS*\n\nDokumentasi, FAQ, dan glosarium:",
            guide_menu_keyboard())
        return

    # ── ❓ SUPPORT ────────────────────────────────────────────────────────────
    if text == "❓ Support":
        await _send(update,
            f"❓ *Support GAS*\n\nTim support siap 24/7:",
            support_menu_keyboard())
        return

    # Unknown text — log and ignore
    logger.warning("unhandled_text", user_id=user.id, text=text)
    print(f"[UNHANDLED TEXT] uid={user.id} text={text!r}")


# ── Inline Callback Dispatcher ─────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data
    user  = update.effective_user
    logger.info("callback", user_id=user.id, data=data)

    # ══ LINK ACCOUNT ══════════════════════════════════════════════════════════
    if data == "do_link":
        code     = await generate_link_code(user.id)
        link_url = f"{SITE_URL}/link-tg?code={code}"
        await query.message.reply_text(
            f"🔗 *Hubungkan Akun GAS*\n\n"
            f"Login di [gasstrategyai\\.xyz]({SITE_URL}) lalu buka link ini:\n\n"
            f"`{link_url}`\n\n_Berlaku 15 menit\\._",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Buka Link", url=link_url)],
                [InlineKeyboardButton("📝 Daftar", url=f"{SITE_URL}/signup")],
            ]))
        return

    # ══ FLOW STARTERS (inline shortcuts) ══════════════════════════════════════
    if data == "flow_signal":
        gas_user_id, plan = await check_bot_access(user.id)
        if not gas_user_id:
            await _edit(query, format_error_md("not_linked")); return
        plan = plan or "free"
        await set_state(user.id, "flow_type", "signal")
        await set_state(user.id, "plan", plan)
        await _edit(query,
            f"📊 *Signal AI*\n\nPilih kategori market:",
            market_category_keyboard("signal", plan))
        return

    # ══ NAV PAIRS (back to pair list of last category) ════════════════════════
    if data.startswith("nav_pairs_"):
        parts     = data.split("_", 2)
        flow_type = parts[2] if len(parts) > 2 else await get_state(user.id, "flow_type", "analysis")
        cat       = await get_state(user.id, "flow_cat", "FOREX")
        plan      = await get_state(user.id, "plan", "free")
        cat_label  = _esc(CAT_LABELS.get(cat, cat))
        flow_label = _esc(_FLOW_LABELS.get(flow_type, flow_type))
        flow_emoji = {"signal": "📊", "analyst": "👑"}.get(flow_type, "🧠")
        await _edit(query,
            f"{flow_emoji} *{flow_label}* — {cat_label}\n\nPilih pair:",
            pair_keyboard_for_plan(cat, flow_type, plan))
        return

    # ══ NAV MARKET (back to market picker) ════════════════════════════════════
    if data.startswith("nav_market"):
        parts     = data.split("_", 2)
        flow_type = parts[2] if len(parts) > 2 else await get_state(user.id, "flow_type", "analysis")
        plan      = await get_state(user.id, "plan", "free")
        await set_state(user.id, "flow_type", flow_type)
        flow_label = _esc(_FLOW_LABELS.get(flow_type, "Analisis"))
        await _edit(query,
            f"*{flow_label}*\n\nPilih kategori market:",
            market_category_keyboard(flow_type, plan))
        return

    # ══ MARKET CATEGORY ═══════════════════════════════════════════════════════
    if data.startswith("mkt_cat_"):
        # mkt_cat_{CAT}_{flow_type}
        parts     = data.replace("mkt_cat_", "").split("_", 1)
        cat       = parts[0]
        flow_type = parts[1] if len(parts) > 1 else await get_state(user.id, "flow_type", "analysis")
        plan      = await get_state(user.id, "plan", "free")
        await set_state(user.id, "flow_cat", cat)
        await set_state(user.id, "flow_type", flow_type)

        cat_label  = _esc(CAT_LABELS.get(cat, cat))
        flow_label = _esc(_FLOW_LABELS.get(flow_type, flow_type))
        cfg        = get_plan_cfg(plan)

        # Gate: category not allowed for this plan
        if cat not in cfg["cats"]:
            upgrade_to = cfg.get("upgrade_to", "plus")
            await query.answer(
                f"🔒 {CAT_LABELS.get(cat, cat)} tersedia mulai plan {upgrade_to.title()}. Upgrade dulu!",
                show_alert=True
            )
            return

        flow_emoji = {"signal": "📊", "analyst": "👑"}.get(flow_type, "🧠")
        await _edit(query,
            f"{flow_emoji} *{flow_label}* — {cat_label}\n\nPilih pair:",
            pair_keyboard_for_plan(cat, flow_type, plan))
        return

    # ══ PAIR SELECTION ════════════════════════════════════════════════════════
    if data.startswith("mkt_pair_"):
        # mkt_pair_{PAIR}_{flow_type}
        rest      = data.replace("mkt_pair_", "")
        parts     = rest.rsplit("_", 1)
        pair      = parts[0]
        flow_type = parts[1] if len(parts) > 1 else await get_state(user.id, "flow_type", "analysis")
        plan      = await get_state(user.id, "plan", "free")
        cfg       = get_plan_cfg(plan)

        # Gate: pair locked for this plan
        limit_pairs = cfg.get("limit_pairs")
        if limit_pairs and pair not in limit_pairs:
            upgrade_to = cfg.get("upgrade_to", "essential")
            await query.answer(
                f"🔒 Pair {pair} tersedia mulai plan {upgrade_to.title()}. Upgrade dulu!",
                show_alert=True
            )
            return

        await set_state(user.id, "selected_pair", pair)
        flow_label = _esc(_FLOW_LABELS.get(flow_type, flow_type))
        await _edit(query,
            f"*{flow_label}*\n\n"
            f"Pair: *{_esc(pair.upper())}*\n\nPilih gaya trading:",
            style_keyboard(pair, flow_type, plan))
        return

    # ══ POLYMARKET ════════════════════════════════════════════════════════════
    if data == "mkt_polymarket":
        await _edit(query,
            f"🎲 *Polymarket Intelligence*\n\n"
            f"Prediksi pasar terkini \\(probabilitas\\):\n\n"
            f"₿ *BTC \\>\\$100k Q2 2025?*\n"
            f"  `░░░░░░░░░░` Tap untuk lihat odds\n\n"
            f"⬡ *ETH \\>\\$5k in 2025?*\n"
            f"  `░░░░░░░░░░` Tap untuk lihat odds\n\n"
            f"🏛 *Fed Rate Cut March 2025?*\n"
            f"  `░░░░░░░░░░` Tap untuk lihat odds\n\n"
            f"📉 *US Recession 2025?*\n"
            f"  `░░░░░░░░░░` Tap untuk lihat odds\n\n"
            f"_Data real\\-time di Polymarket\\.com_",
            polymarket_keyboard())
        return

    if data.startswith("poly_"):
        market_info = {
            "poly_btc100k":   ("₿ BTC >$100k Q2 2025",   "https://polymarket.com/event/bitcoin-100k"),
            "poly_eth5k":     ("⬡ ETH >$5k in 2025",      "https://polymarket.com/event/ethereum-5k"),
            "poly_fedcut":    ("🏛 Fed Rate Cut March",    "https://polymarket.com"),
            "poly_recession": ("📉 US Recession 2025",     "https://polymarket.com"),
        }
        info = market_info.get(data, ("Market", "https://polymarket.com"))
        title, url = info
        await _edit(query,
            f"🎲 *{_esc(title)}*\n\n"
            f"Lihat probabilitas real\\-time dan trading flow\n"
            f"di Polymarket untuk data prediksi\\.\n\n"
            f"💡 *Cara pakai untuk trading:*\n"
            f"• Odds tinggi = market yakin → trade searah\n"
            f"• Odds berubah cepat = volatilitas tinggi\n"
            f"• Gunakan sebagai konfirmasi fundamental",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Buka Polymarket", url=url)],
                [InlineKeyboardButton("🔙 Polymarket", callback_data="mkt_polymarket")],
            ]))
        return

    # ══ STYLE → CONFIRM ═══════════════════════════════════════════════════════
    if data.startswith("style_"):
        # style_{flow_type}_{style_id}_{pair}
        parts = data.split("_", 3)
        if len(parts) < 4:
            return
        _, flow_type, style_id, pair = parts

        gas_user_id, plan = await check_bot_access(user.id)
        if not gas_user_id:
            await _edit(query, format_error_md("not_linked")); return

        plan = plan or "free"
        cfg  = get_plan_cfg(plan)

        # Gate: style not in plan
        if style_id not in cfg.get("styles", set()):
            upgrade_to = cfg.get("upgrade_to", "plus")
            await query.answer(
                f"🔒 Style {style_id} tersedia mulai plan {upgrade_to.title()}.",
                show_alert=True
            )
            return

        credits     = await get_user_credits(gas_user_id)
        cost        = STYLE_COST.get(style_id, 3)
        if plan in ("free", "trial"):
            cost = FREE_COST_OVERRIDE

        flow_label  = _esc(_FLOW_LABELS.get(flow_type, flow_type))
        style_label = STYLE_LABELS.get(style_id, _esc(style_id.title()))
        ai_label    = {"basic":"⚙️ Basic","advanced":"🚀 Advanced","pro":"💎 Pro","ultra":"⚡ Ultra"}.get(cfg["ai_tier"],"AI")
        cache_note  = "No cache" if cfg["cache_ttl"] == 0 else f"Cache {cfg['cache_ttl']}s"

        if credits < cost:
            await _edit(query, format_error_md("no_credits"),
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 Topup", url=f"{SITE_URL}/pricing")],
                    [InlineKeyboardButton("🔙 Market", callback_data=f"nav_market_{flow_type}")],
                ])); return

        await _edit(query,
            f"🎯 *Konfirmasi*\n\n"
            f"Mode:   *{flow_label}*\n"
            f"Pair:   *{_esc(pair.upper())}*\n"
            f"Style:  *{style_label}*\n"
            f"AI:     *{ai_label}*\n"
            f"Cache:  *{_esc(cache_note)}*\n"
            f"Biaya:  *{_esc(str(cost))} credit*\n"
            f"Sisa:   *{_esc(str(credits))} credit*\n\n"
            f"_Lanjutkan?_",
            confirm_analysis_keyboard(pair, style_id, cost, flow_type))
        return

    # ══ EXECUTE ANALYSIS ══════════════════════════════════════════════════════
    if data.startswith("exec_"):
        # exec_{flow_type}_{pair}_{style}
        parts = data.split("_", 3)
        if len(parts) < 4:
            return
        _, flow_type, pair, style = parts

        gas_user_id, plan = await check_bot_access(user.id)
        if not gas_user_id:
            await _edit(query, format_error_md("not_linked")); return

        await _run_analysis(query, gas_user_id, pair, style, flow_type, plan or "free")
        return

    # ══ NEWS ══════════════════════════════════════════════════════════════════
    if data == "m_news":
        await _edit(query,
            f"📰 *News & Intelligence*\n\nPilih kategori:",
            news_menu_keyboard())
        return

    if data == "m_news_calendar":
        events = await signal_cache.get_feed("calendar")
        await _edit(query,
            format_calendar_md(events or []),
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="m_news_calendar"),
                 InlineKeyboardButton("🌐 Dashboard", url=SITE_URL)],
                [InlineKeyboardButton("🔙 News", callback_data="m_news")],
            ]))
        return

    if data == "m_news_urgent":
        await _edit(query,
            f"🚨 *High Impact News*\n\n"
            f"🔴 NFP \\(USD\\) — Pengaruh SANGAT TINGGI\n"
            f"🔴 FOMC Minutes \\(USD\\) — SANGAT TINGGI\n"
            f"🟡 ECB Rate \\(EUR\\) — TINGGI\n"
            f"🟡 BOE Rate \\(GBP\\) — TINGGI\n\n"
            f"_Update real\\-time di [GAS Calendar]({SITE_URL}/dashboard)_",
            _back_btn("🔙 News", "m_news"))
        return

    if data == "m_news_sentiment":
        await _edit(query,
            f"📊 *Sentimen Global*\n\n"
            f"🟢 *USD*: Bullish \\| Fed hawkish\n"
            f"🔴 *EUR*: Bearish \\| ECB dovish\n"
            f"🟡 *GBP*: Neutral \\| BOE data\\-dependent\n"
            f"🟢 *GOLD*: Bullish \\| Safe\\-haven\n"
            f"🟡 *BTC*: Konsolidasi \\| On\\-chain bullish\n"
            f"🟢 *ETH*: Bullish \\| ETF flow positif\n\n"
            f"_Update tiap 5 menit via GAS AI Feed_",
            _back_btn("🔙 News", "m_news"))
        return

    if data == "m_news_fundamental":
        await _edit(query,
            f"🔗 *Fundamental Summary*\n\n"
            f"📌 *Macro Themes:*\n"
            f"• Fed hawkish → USD kuat\n"
            f"• China stimulus → commodity bullish\n"
            f"• Risk\\-off: GOLD \\+ JPY menguat\n"
            f"• OPEC\\+ supply cut → WTI \\>\\$80\n"
            f"• Crypto ETF flow positif\n\n"
            f"_[Laporan lengkap]({SITE_URL}/dashboard) di GAS Dashboard_",
            _back_btn("🔙 News", "m_news"))
        return

    if data == "m_news_macro":
        await _edit(query,
            f"💎 *Intisari Makro Hari Ini*\n\n"
            f"🌍 Global: Risk sentiment mixed\n"
            f"🇺🇸 USD: Strong, labor data solid\n"
            f"🇪🇺 EUR: Under pressure, weak PMI\n"
            f"🥇 GOLD: Safe\\-haven demand kuat\n"
            f"₿ BTC: Konsolidasi, ETF inflow positif\n"
            f"🐸 MEME: High volatility, momentum check\n\n"
            f"_Sumber: GAS AI Feed \\| Update setiap jam_",
            _back_btn("🔙 News", "m_news"))
        return

    # ══ TOOLS / CALCULATOR ════════════════════════════════════════════════════
    if data in ("m_tools", "m_calc"):
        await _edit(query,
            f"🧮 *Trading Tools*\n\nPilih kalkulator:",
            tools_menu_keyboard())
        return

    if data == "m_calc_pos_size":
        await _edit(query,
            f"⚖️ *Lot Size Calculator*\n\n"
            f"*Formula:*\n"
            f"```\nLot = (Balance × Risk%) ÷ (SL_pips × Pip_Value)\n```\n\n"
            f"*Contoh \\(XAUUSD\\):*\n"
            f"```\nBalance : $1,000\nRisk    : 1% = $10\nSL      : 15 pips  \nPip Val : $1/pip\n\nLot = 10 ÷ (15×1) = 0.67\n```\n\n"
            f"_Kalkulator interaktif di [GAS Dashboard]({SITE_URL}/dashboard)_",
            _back_btn("🔙 Tools", "m_tools"))
        return

    if data == "m_calc_margin_leverage":
        await _edit(query,
            f"🎯 *Margin & Leverage*\n\n"
            f"```\nMargin = (Lot×Contract×Price) ÷ Leverage\n\n1:10  → Conservative (prop)\n1:50  → Moderate\n1:100 → Standard retail\n1:500 → High risk ⚠\n```",
            _back_btn("🔙 Tools", "m_tools"))
        return

    if data == "m_calc_pivot":
        await _edit(query,
            f"📈 *Pivot Point*\n\n"
            f"```\nP  = (H + L + C) ÷ 3\nR1 = (2×P) - L\nS1 = (2×P) - H\nR2 = P + (H - L)\nS2 = P - (H - L)\n```\n\n"
            f"_Auto\\-calc di [GAS Dashboard]({SITE_URL}/dashboard)_",
            _back_btn("🔙 Tools", "m_tools"))
        return

    if data == "m_calc_time_converter":
        await _edit(query, format_sessions_md(), _back_btn("🔙 Tools", "m_tools"))
        return

    if data == "m_calc_pip_value":
        await _edit(query,
            f"💱 *Nilai Pip \\(per 0\\.01 lot\\)*\n\n"
            f"```\nEURUSD → $0.10/pip\nGBPUSD → $0.10/pip\nUSDJPY → $0.10/pip\nXAUUSD → $1.00/pip\nBTCUSD → $0.10/pip\nDOGEUSDT→ $0.001/pip\n```",
            _back_btn("🔙 Tools", "m_tools"))
        return

    if data == "m_calc_recovery":
        await _edit(query,
            f"🛠️ *Recovery Calculator*\n\n"
            f"```\nDD 10% → Need +11.1% to recover\nDD 20% → Need +25.0% to recover\nDD 30% → Need +42.9% to recover\nDD 50% → Need +100% to recover\n```\n\n"
            f"⚠️ _Jaga max DD di bawah 20%\\!_",
            _back_btn("🔙 Tools", "m_tools"))
        return

    if data == "m_calc_rr":
        await _edit(query,
            f"⚡ *R:R Calculator*\n\n"
            f"*Formula:*\n"
            f"```\nRR = (TP - Entry) ÷ (Entry - SL)\n\nMinimum RR = 1:2\nIdeal RR   = 1:3 atau lebih\n```\n\n"
            f"*Contoh XAUUSD:*\n"
            f"```\nEntry : 2050.00\nSL    : 2045.00 (5 pips)\nTP    : 2065.00 (15 pips)\nRR    : 15/5 = 1:3 ✓\n```",
            _back_btn("🔙 Tools", "m_tools"))
        return

    # ══ JOURNAL ═══════════════════════════════════════════════════════════════
    if data == "m_jurnal":
        await _edit(query,
            f"🧾 *Trade Journal*\n\nPilih menu:",
            journal_menu_keyboard())
        return

    if data == "m_jurnal_new":
        await _edit(query,
            f"🆕 *Catat Trade Baru*\n\n"
            f"Catat di [GAS Journal]({SITE_URL}/dashboard)\\.",
            _back_btn("🔙 Journal", "m_jurnal"))
        return

    if data == "m_jurnal_stats":
        gas_user_id, plan = await check_bot_access(user.id)
        if not gas_user_id:
            await _edit(query, format_error_md("not_linked")); return
        await _edit(query,
            f"📊 *Statistik Win\\-Rate*\n\n"
            f"Data lengkap di [GAS Dashboard]({SITE_URL}/dashboard)\\.",
            _back_btn("🔙 Journal", "m_jurnal"))
        return

    if data == "m_jurnal_history":
        await _edit(query,
            f"📝 *Riwayat & Backtest*\n\n"
            f"History di [GAS Journal]({SITE_URL}/dashboard)\\.",
            _back_btn("🔙 Journal", "m_jurnal"))
        return

    if data == "m_jurnal_psycho":
        await _edit(query,
            f"🧠 *Audit Psikologi*\n\n"
            f"Checklist sebelum entry:\n"
            f"✅ Tidak FOMO atau revenge trade\n"
            f"✅ Setup valid sudah konfirmasi\n"
            f"✅ Risk sudah dihitung\n"
            f"✅ Emosi stabil, tidak terburu\n\n"
            f"_Audit lengkap di [GAS Dashboard]({SITE_URL}/dashboard)_",
            _back_btn("🔙 Journal", "m_jurnal"))
        return

    if data == "m_jurnal_export":
        await _edit(query,
            f"📂 *Export Jurnal*\n\n"
            f"Export CSV/PDF di [GAS Journal]({SITE_URL}/dashboard)\\.",
            _back_btn("🔙 Journal", "m_jurnal"))
        return

    # ══ GUIDE ═════════════════════════════════════════════════════════════════
    if data == "m_guide":
        await _edit(query,
            f"📘 *Panduan GAS*\n\nPilih topik:",
            guide_menu_keyboard())
        return

    if data == "m_guide_setup":
        await _edit(query,
            f"📖 *Setup Awal*\n\n"
            f"1\\. Daftar di [gasstrategyai\\.xyz]({SITE_URL}/signup)\n"
            f"2\\. Pilih plan \\(Free → Ultimate\\)\n"
            f"3\\. /link → buka di browser\n"
            f"4\\. /start → terhubung ✅\n\n"
            f"*Setup MT5 EA:*\n"
            f"• Download EA dari dashboard\n"
            f"• Install di MT5, set API key",
            _back_btn("🔙 Guide", "m_guide"))
        return

    if data == "m_guide_faq":
        await _edit(query,
            f"❓ *FAQ*\n\n"
            f"*Credits habis cepat?*\n"
            f"_Cache 30s berbagi antar user_\n\n"
            f"*Bot tidak respons?*\n"
            f"_Cek /status — credits harus \\> 0_\n\n"
            f"*Cara upgrade?*\n"
            f"_Tap 💎 Upgrade di keyboard bawah_\n\n"
            f"*Meme coins tersedia?*\n"
            f"_Ya\\! Signal → Meme Coins untuk DOGE/SHIB/PEPE_",
            _back_btn("🔙 Guide", "m_guide"))
        return

    if data == "m_guide_glossary":
        await _edit(query,
            f"🌐 *Glossarium SMC & AI*\n\n"
            f"*BOS* — Break of Structure\n"
            f"*MSS* — Market Structure Shift\n"
            f"*OB* — Order Block\n"
            f"*FVG* — Fair Value Gap\n"
            f"*LQ* — Liquidity Zone\n"
            f"*POI* — Point of Interest\n"
            f"*PDH/PDL* — Previous Day High/Low\n"
            f"*RR* — Risk:Reward Ratio\n"
            f"*CHoCH* — Change of Character",
            _back_btn("🔙 Guide", "m_guide"))
        return

    if data in ("m_guide_search",):
        await _edit(query,
            f"🔍 *Dokumentasi Fitur*\n\n"
            f"Akses dokumentasi lengkap di [GAS Guide]({SITE_URL}/dashboard)\\.",
            _back_btn("🔙 Guide", "m_guide"))
        return

    # ══ SUPPORT ═══════════════════════════════════════════════════════════════
    if data == "m_support":
        await _edit(query,
            f"❓ *Support GAS*\n\nPilih bantuan:",
            support_menu_keyboard())
        return

    if data == "m_support_live_chat":
        await _edit(query,
            f"💬 *Live Chat*\n\n"
            f"Tim support 24/7:\n"
            f"• [GAS Dashboard]({SITE_URL}/dashboard)\n"
            f"• Email: support@gasstrategyai\\.xyz",
            _back_btn("🔙 Support", "m_support"))
        return

    if data in ("m_support_new_ticket", "m_support_check_ticket", "m_support_feedback"):
        await _edit(query,
            f"❓ *Support Center*\n\n"
            f"Buka tiket di [GAS Support]({SITE_URL}/dashboard)\\.",
            _back_btn("🔙 Support", "m_support"))
        return

    # ══ UPGRADE ═══════════════════════════════════════════════════════════════
    if data in ("upgrade_now", "u_menu") or data.startswith("m_buy_"):
        await query.message.reply_text(
            f"💎 *Upgrade Plan GAS*\n\n"
            f"Detail di [GAS Pricing]({SITE_URL}/pricing)",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=plan_menu_keyboard())
        return

    # ══ LEGACY CALLBACKS (backward compat) ════════════════════════════════════
    if data in ("main_home", "m_main_menu"):
        gas_user_id, plan = await check_bot_access(user.id)
        credits = await get_user_credits(gas_user_id) if gas_user_id else 0
        xp      = await get_user_xp(gas_user_id) if gas_user_id else 0
        await query.message.reply_text(
            _welcome_text(plan or "free", credits, user.first_name, xp),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard())
        return

    if data == "cancel_analysis":
        flow_type = await get_state(user.id, "flow_type", "analysis")
        await _edit(query,
            f"❌ *Analisis Dibatalkan*\n\nPilih pair lain:",
            market_category_keyboard(flow_type))
        return

    # ══ FALLBACK ══════════════════════════════════════════════════════════════
    logger.warning("unhandled_callback", data=data, user=user.id)
    print(f"[UNHANDLED CB] uid={user.id} data={data!r}")
    await query.answer("⏳ Fitur segera hadir!", show_alert=False)


# ── Register all handlers ──────────────────────────────────────────────────────

def register_handlers(application):
    # Commands
    application.add_handler(CommandHandler("start",    start))
    application.add_handler(CommandHandler("menu",     menu_command))
    application.add_handler(CommandHandler("signal",   signal_command))
    application.add_handler(CommandHandler("analysis", analysis_command))
    application.add_handler(CommandHandler("analyst",  analyst_command))
    application.add_handler(CommandHandler("market",   market_command))
    application.add_handler(CommandHandler("tools",    tools_command))
    application.add_handler(CommandHandler("plan",     plan_command))
    application.add_handler(CommandHandler("journal",  journal_command))
    application.add_handler(CommandHandler("news",     news_command))
    application.add_handler(CommandHandler("help",     help_command))
    application.add_handler(CommandHandler("support",  support_command))
    application.add_handler(CommandHandler("link",     link_command))
    application.add_handler(CommandHandler("status",   status_command))
    # Inline callbacks
    application.add_handler(CallbackQueryHandler(handle_callback))
    # ReplyKeyboard text (must be last — lowest priority)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_message,
    ))
