from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# =================================================================
# 3. Main Menu Keyboards (m_)
# =================================================================

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main Menu (REPLY KEYBOARD - Persistent buttons at bottom)."""
    keyboard = [
        [KeyboardButton("👤 My Dash"), KeyboardButton("📰 News"), KeyboardButton("✨ Upgrade")],
        [KeyboardButton("📝 Journal"), KeyboardButton("🎓 Academy"), KeyboardButton("💼 Plan")],
        [KeyboardButton("🧮 Calculator"), KeyboardButton("📖 Guide"), KeyboardButton("❓ Support")],
        [KeyboardButton("📊 Golden AI Strategy")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def main_menu_inline_keyboard() -> InlineKeyboardMarkup:
    """Keyboard Inline Menu Utama untuk dashboard."""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh Dash", callback_data="m_mydash"),
            InlineKeyboardButton("📰 News", callback_data="m_news"),
            InlineKeyboardButton("✨ Upgrade", callback_data="u_menu"),
        ],
        [
            InlineKeyboardButton("📒 Journal", callback_data="m_jurnal"),
            InlineKeyboardButton("🎓 Academy", callback_data="m_academy"),
            InlineKeyboardButton("🗺 Plan", callback_data="m_plan"),
        ],
        [
            InlineKeyboardButton("🧮 Calculator", callback_data="m_calc"),
            InlineKeyboardButton("📘 Guide", callback_data="m_guide"),
            InlineKeyboardButton("❓ Support", callback_data="m_support"),
        ],
        [
            InlineKeyboardButton("🤖 Golden AI Strategy", callback_data="m_ai_analyst"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# =================================================================
# 5. Advanced Submenu Keyboards (Ultimate Golden AI Edition)
# =================================================================

def news_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard Menu News - Navigasi Intelijen Fundamental."""
    keyboard = [
        [InlineKeyboardButton("📅 Kalender Ekonomi Dunia", callback_data="m_news_calendar")],
        [InlineKeyboardButton("🚨 High Impact News Alert", callback_data="m_news_urgent")],
        [InlineKeyboardButton("📊 Analisis Sentimen Global", callback_data="m_news_pair_analysis")],
        [InlineKeyboardButton("🔗 Fundamental Summary Report", callback_data="m_news_source")],
        [InlineKeyboardButton("🔔 Set Pengingat Berita", callback_data="m_news_set_alert")],
        [InlineKeyboardButton("💎 Intisari Makro Hari Ini", callback_data="m_news_daily_macro")],
        [InlineKeyboardButton("⬅️ Kembali ke Markas Utama", callback_data="m_main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def jurnal_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard Menu Jurnal - Arsip Kedisiplinan & Statistik."""
    keyboard = [
        [InlineKeyboardButton("🆕 Catat Eksekusi Trade Baru", callback_data="m_jurnal_new")],
        [InlineKeyboardButton("📊 Dashboard Statistik Win-Rate", callback_data="m_jurnal_stats")],
        [InlineKeyboardButton("📝 Review Riwayat & Backtest", callback_data="m_jurnal_history")],
        [InlineKeyboardButton("🧠 Audit Psikologi & Emosi", callback_data="m_jurnal_psycho")],
        [InlineKeyboardButton("📂 Ekspor Data Jurnal (CSV/PDF)", callback_data="m_jurnal_export")],
        [InlineKeyboardButton("⬅️ Kembali ke Markas Utama", callback_data="m_main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def plan_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard Menu Plan - Blueprint Perang & Validasi AI."""
    keyboard = [
        [InlineKeyboardButton("🎯 Strategi Aktif: Golden Plan", callback_data="m_plan_edit")],
        [InlineKeyboardButton("🔍 Validasi Setup Vision AI", callback_data="m_plan_validate")],
        [InlineKeyboardButton("🏗️ Review Zona SMC & OrderBlock", callback_data="m_plan_review_sd")],
        [InlineKeyboardButton("⚖️ Kalkulator R:R Multi-Layer", callback_data="m_plan_rr_calc")],
        [InlineKeyboardButton("⚙️ Log & Audit Pelanggaran Plan", callback_data="m_plan_violation_log")],
        [InlineKeyboardButton("🚀 Optimasi Target Profit", callback_data="m_plan_optimize")],
        [InlineKeyboardButton("⬅️ Kembali ke Markas Utama", callback_data="m_main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def calc_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard Menu Calc - Senjata Presisi Risk Management."""
    keyboard = [
        [InlineKeyboardButton("⚖️ Kalkulator Lot Size Militer", callback_data="m_calc_pos_size")],
        [InlineKeyboardButton("🎯 Analisis Margin & Leverage", callback_data="m_calc_margin_leverage")],
        [InlineKeyboardButton("📈 Pivot Point & S/R Daily", callback_data="m_calc_pivot")],
        [InlineKeyboardButton("⏳ Konverter Waktu Sesi Global", callback_data="m_calc_time_converter")],
        [InlineKeyboardButton("💱 Kalkulator Nilai Pip Presisi", callback_data="m_calc_pip_value")],
        [InlineKeyboardButton("🛠️ Tools Pemulihan Modal (Recovery)", callback_data="m_calc_recovery")],
        [InlineKeyboardButton("⬅️ Kembali ke Markas Utama", callback_data="m_main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def guide_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard Menu Guide - Perpustakaan Pengetahuan Golden AI."""
    keyboard = [
        [InlineKeyboardButton("📖 Panduan Setup Sistem Awal", callback_data="m_guide_setup")],
        [InlineKeyboardButton("❓ FAQ: Solusi Masalah Cepat", callback_data="m_guide_faq")],
        [InlineKeyboardButton("🌐 Glossarium Istilah SMC & AI", callback_data="m_guide_glossary")],
        [InlineKeyboardButton("🔍 Dokumentasi Fitur Vision", callback_data="m_guide_search")],
        [InlineKeyboardButton("💬 Hubungi Support Spesialis", callback_data="m_guide_contact_support")],
        [InlineKeyboardButton("⬅️ Kembali ke Markas Utama", callback_data="m_main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def support_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard Menu Support - Pusat Komando Bantuan."""
    keyboard = [
        [InlineKeyboardButton("💬 Live Chat Teknisi (24/7)", callback_data="m_support_live_chat")],
        [InlineKeyboardButton("✉️ Buka Tiket Bantuan Baru", callback_data="m_support_new_ticket")],
        [InlineKeyboardButton("🎫 Pantau Status Tiket Anda", callback_data="m_support_check_ticket")],
        [InlineKeyboardButton("⚙️ Kirim Kritik & Saran", callback_data="m_support_feedback")],
        [InlineKeyboardButton("❓ Bantuan Darurat (Urgent)", callback_data="m_support_urgent_faq")],
        [InlineKeyboardButton("⬅️ Kembali ke Markas Utama", callback_data="m_main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def mydash_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard Menu Mydash - Refleksi Portofolio & Performa."""
    keyboard = [
        [InlineKeyboardButton("🔭 Dashboard Overview Utama", callback_data="m_mydash_overview")],
        [InlineKeyboardButton("📈 Kurva Performa & Ekuitas", callback_data="m_mydash_performance")],
        [InlineKeyboardButton("🎯 Monitoring Target Profit", callback_data="m_mydash_goals")],
        [InlineKeyboardButton("⚙️ Pengaturan & Kustomisasi Bot", callback_data="m_mydash_settings")],
        [InlineKeyboardButton("🔑 Manajemen Lisensi & Akun", callback_data="m_mydash_account")],
        [InlineKeyboardButton("👤 Lihat Trader DNA Saya", callback_data="i_view_profile")],
        [InlineKeyboardButton("⬅️ Markas Utama (Dashboard)", callback_data="m_main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def academy_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard Menu Academy - Kawah Candradimuka Trader."""
    keyboard = [
        [InlineKeyboardButton("📚 Kursus Masterclass SMC", callback_data="m_academy_courses")],
        [InlineKeyboardButton("🎥 Rekaman Live Trading & Analisa", callback_data="m_academy_videos")],
        [InlineKeyboardButton("📖 Artikel Strategi Eksklusif", callback_data="m_academy_articles")],
        [InlineKeyboardButton("🧠 Uji Mental & Kuis Psikologi", callback_data="m_academy_quizzes")],
        [InlineKeyboardButton("🏆 Tantangan Trader (Challenge)", callback_data="m_academy_challenges")],
        [InlineKeyboardButton("⬅️ Kembali ke Markas Utama", callback_data="m_main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)
