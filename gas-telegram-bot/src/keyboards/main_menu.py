from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

SITE_URL = "https://www.gasstrategyai.xyz"

# ──────────────────────────────────────────────────────────────────────────────
# PRIMARY NAV — ReplyKeyboard (persistent bottom bar, always visible)
# ──────────────────────────────────────────────────────────────────────────────

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """10-button grid: Signal + Analisa + Analyst + Market + all tools."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("📊 Signal"),   KeyboardButton("🧠 Analisa")],
            [KeyboardButton("👑 Analyst"),  KeyboardButton("🌍 Market")],
            [KeyboardButton("📰 News"),     KeyboardButton("💎 Upgrade")],
            [KeyboardButton("🧾 Journal"),  KeyboardButton("🧮 Tools")],
            [KeyboardButton("📘 Guide"),    KeyboardButton("❓ Support")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


# ──────────────────────────────────────────────────────────────────────────────
# INLINE keyboards for section detail views
# ──────────────────────────────────────────────────────────────────────────────

def main_menu_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline shortcut — used in /status reply."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Signal AI",  callback_data="flow_signal"),
         InlineKeyboardButton("💳 Topup",      url=f"{SITE_URL}/pricing")],
    ])


def news_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Kalender Ekonomi Hari Ini",  callback_data="m_news_calendar")],
        [InlineKeyboardButton("🚨 High Impact Alert",          callback_data="m_news_urgent")],
        [InlineKeyboardButton("📊 Sentimen Global",            callback_data="m_news_sentiment")],
        [InlineKeyboardButton("🔗 Fundamental Summary",        callback_data="m_news_fundamental")],
        [InlineKeyboardButton("💎 Intisari Makro Hari Ini",    callback_data="m_news_macro")],
        [InlineKeyboardButton("🎲 Polymarket Odds",            callback_data="mkt_polymarket")],
        [InlineKeyboardButton("🏠 Menu Utama",                 callback_data="m_main_menu")],
    ])


def tools_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚖️ Lot Size Calculator",         callback_data="m_calc_pos_size")],
        [InlineKeyboardButton("🎯 Margin & Leverage",           callback_data="m_calc_margin_leverage")],
        [InlineKeyboardButton("📈 Pivot Point & S/R",           callback_data="m_calc_pivot")],
        [InlineKeyboardButton("⏳ Sesi Trading Global",         callback_data="m_calc_time_converter")],
        [InlineKeyboardButton("💱 Nilai Pip",                   callback_data="m_calc_pip_value")],
        [InlineKeyboardButton("🛠️ Recovery Calculator",         callback_data="m_calc_recovery")],
        [InlineKeyboardButton("⚡ R:R Calculator",              callback_data="m_calc_rr")],
        [InlineKeyboardButton("🏠 Menu Utama",                  callback_data="m_main_menu")],
    ])


def journal_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🆕 Catat Trade Baru",            callback_data="m_jurnal_new")],
        [InlineKeyboardButton("📊 Statistik Win-Rate",          callback_data="m_jurnal_stats")],
        [InlineKeyboardButton("📝 Riwayat & Backtest",          callback_data="m_jurnal_history")],
        [InlineKeyboardButton("🧠 Audit Psikologi",             callback_data="m_jurnal_psycho")],
        [InlineKeyboardButton("📂 Ekspor Jurnal (CSV/PDF)",     callback_data="m_jurnal_export")],
        [InlineKeyboardButton("🏠 Menu Utama",                  callback_data="m_main_menu")],
    ])


def guide_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Panduan Setup Awal",          callback_data="m_guide_setup")],
        [InlineKeyboardButton("❓ FAQ",                         callback_data="m_guide_faq")],
        [InlineKeyboardButton("🌐 Glossarium SMC & AI",         callback_data="m_guide_glossary")],
        [InlineKeyboardButton("🔍 Dokumentasi Fitur",           callback_data="m_guide_search")],
        [InlineKeyboardButton("🏠 Menu Utama",                  callback_data="m_main_menu")],
    ])


def support_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Live Chat (24/7)",            callback_data="m_support_live_chat")],
        [InlineKeyboardButton("✉️ Buka Tiket Baru",            callback_data="m_support_new_ticket")],
        [InlineKeyboardButton("🎫 Cek Status Tiket",           callback_data="m_support_check_ticket")],
        [InlineKeyboardButton("⚙️ Kirim Feedback",             callback_data="m_support_feedback")],
        [InlineKeyboardButton("🏠 Menu Utama",                  callback_data="m_main_menu")],
    ])


# Keep these for backward-compat callbacks
def jurnal_menu_keyboard() -> InlineKeyboardMarkup:
    return journal_menu_keyboard()

def plan_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔵 Essential — Rp 29.900/bln",   url=f"{SITE_URL}/pricing")],
        [InlineKeyboardButton("➕ Plus — Rp 59.900/bln",        url=f"{SITE_URL}/pricing")],
        [InlineKeyboardButton("💎 Premium — Rp 119.900/bln",    url=f"{SITE_URL}/pricing")],
        [InlineKeyboardButton("👑 Ultimate — Rp 199.900/bln",   url=f"{SITE_URL}/pricing")],
        [InlineKeyboardButton("💳 Bayar USDT (TRC20/ERC20)",    url=f"{SITE_URL}/pricing")],
        [InlineKeyboardButton("🏠 Menu Utama",                   callback_data="m_main_menu")],
    ])

def calc_menu_keyboard() -> InlineKeyboardMarkup:
    return tools_menu_keyboard()

def mydash_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔭 Dashboard Overview",          callback_data="m_mydash_overview")],
        [InlineKeyboardButton("📈 Kurva Performa & Ekuitas",    callback_data="m_mydash_performance")],
        [InlineKeyboardButton("🎯 Target Profit Monitor",       callback_data="m_mydash_goals")],
        [InlineKeyboardButton("⚙️ Pengaturan Bot",              callback_data="m_mydash_settings")],
        [InlineKeyboardButton("🔑 Manajemen Lisensi & Akun",   callback_data="m_mydash_account")],
        [InlineKeyboardButton("👤 Trader DNA Saya",             callback_data="i_view_profile")],
    ])

def academy_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Kursus SMC Masterclass",      callback_data="m_academy_courses")],
        [InlineKeyboardButton("🎥 Rekaman Live Trading",         callback_data="m_academy_videos")],
        [InlineKeyboardButton("📖 Artikel Eksklusif",           callback_data="m_academy_articles")],
        [InlineKeyboardButton("🧠 Kuis Psikologi",              callback_data="m_academy_quizzes")],
        [InlineKeyboardButton("🏆 Trader Challenge",            callback_data="m_academy_challenges")],
    ])
