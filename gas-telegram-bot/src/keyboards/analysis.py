from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import hashlib

# =================================================================
# 2. Post-Active Analysis Keyboards (Pillar Access)
# =================================================================

def active_user_analysis_keyboard(plan_name: str = "PREMIUM") -> InlineKeyboardMarkup:
    """
    Keyboard Utama untuk User yang sudah beli Plan.
    """
    keyboard = [
        [InlineKeyboardButton("📊 Analisa Mandiri", callback_data="a_analisa_mandiri")]
    ]
    
    if plan_name.upper() == "ULTIMATE":
        keyboard.append([InlineKeyboardButton("🔴 Live Trade Tracking", callback_data="a_live_trade_track")])
        keyboard.append([InlineKeyboardButton("🔴 Live Market FX", callback_data="a_live_market_fx")])
        keyboard.append([InlineKeyboardButton("🔴 Live Trade Signal", callback_data="a_live_signal")])
        keyboard.append([InlineKeyboardButton("👨🏻💻 EA Command Center", callback_data="ea_gas_advance")])
    
    keyboard.append([InlineKeyboardButton(f"🚀 Beli BOOST {plan_name}", callback_data=f"u_boost_{plan_name}")])
    keyboard.append([InlineKeyboardButton("⬅️ Menu Utama", callback_data="m_main_menu")])
    
    return InlineKeyboardMarkup(keyboard)

# -----------------------------------------------------------------
# 🔍 FINAL STEP: PILLAR BUTTONS (Triggered after analysis)
# -----------------------------------------------------------------
def analysis_result_pillar_keyboard(analysis_id: int = None) -> InlineKeyboardMarkup:
    """Satu set tombol lengkap untuk akses hasil analisa AI."""
    suffix = f"_{analysis_id}" if analysis_id else ""
    keyboard = [
        [InlineKeyboardButton("🔄 RE-ANALYZE (LIVE)", callback_data="m_ai_analyst")],
        [
            InlineKeyboardButton("🔍 Observasi", callback_data=f"pillar_observasi{suffix}"),
            InlineKeyboardButton("💡 Reasoning", callback_data=f"pillar_reasoning{suffix}")
        ],
        [InlineKeyboardButton("🎯 Trading Plan Executable", callback_data=f"pillar_tradingplan{suffix}")],
        [InlineKeyboardButton("🚀 PREPARE ENTRY (SAFETY CHECK)", callback_data=f"p_prepare_entry{suffix}")],
        [
            InlineKeyboardButton("🛡 Risk", callback_data=f"pillar_riskmanagement{suffix}"),
            InlineKeyboardButton("📝 Journal", callback_data=f"pillar_journalbacktest{suffix}")
        ],
        [InlineKeyboardButton("⚕️ Psychology", callback_data=f"pillar_psychologymindset{suffix}")],
        [InlineKeyboardButton("⬅️ Dashboard Utama", callback_data="m_main_menu")],
        [
            InlineKeyboardButton("👤 My Dash", callback_data="m_mydash"),
            InlineKeyboardButton("📰 News", callback_data="m_news"),
            InlineKeyboardButton("🤖 Strategy", callback_data="m_ai_analyst")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def analysis_progress_keyboard(status: dict) -> InlineKeyboardMarkup:
    """Keyboard progress dengan tombol pillar yang aktif berdasarkan status."""
    pillars = {
        "observation": ("🔍 Observasi", "pillar_observasi"),
        "reasoning": ("💡 Reasoning", "pillar_reasoning"),
        "tradingplan": ("🎯 Trading Plan", "pillar_tradingplan"),
        "riskmanagement": ("🛡 Risk", "pillar_riskmanagement"),
        "journalbacktest": ("📝 Journal", "pillar_journalbacktest"),
        "psychologymindset": ("⚕️ Psychology", "pillar_psychologymindset"),
    }
    
    keyboard = []
    for key, (label, callback) in pillars.items():
        if status.get(key) == "done":
            keyboard.append([InlineKeyboardButton(label, callback_data=callback)])
    
    if status.get("tradingplan") == "done":
        keyboard.append([InlineKeyboardButton("🚀 PREPARE ENTRY", callback_data="p_prepare_entry")])
            
    keyboard.append([InlineKeyboardButton("⬅️ Menu Utama", callback_data="m_main_menu")])
    return InlineKeyboardMarkup(keyboard)

def entry_confirmation_keyboard(analysis_id: int = None) -> InlineKeyboardMarkup:
    """Keyboard konfirmasi setelah pre-trade audit."""
    suffix = f"_{analysis_id}" if analysis_id else ""
    keyboard = [
        [
            InlineKeyboardButton("✅ CONFIRM ENTRY", callback_data=f"p_manual_entry{suffix}"),
            InlineKeyboardButton("❌ CANCEL", callback_data="m_main_menu")
        ],
        [
            InlineKeyboardButton("📝 Edit SL", callback_data=f"p_edit_sl{suffix}"),
            InlineKeyboardButton("🎯 Edit TP", callback_data=f"p_edit_tp{suffix}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# =================================================================
# 12. PSYCHOLOGY JOURNAL KEYBOARDS (PRE-ENTRY)
# =================================================================

def psychology_mental_keyboard() -> InlineKeyboardMarkup:
    """Buttons for selecting mental state before entry."""
    keyboard = [
        [InlineKeyboardButton("🧘 Tenang", callback_data="psy_mental_calm")],
        [InlineKeyboardButton("😑 Bosan", callback_data="psy_mental_bored")],
        [InlineKeyboardButton("🚀 FOMO", callback_data="psy_mental_fomo")],
        [InlineKeyboardButton("😤 Ingin Balas Loss", callback_data="psy_mental_revenge")],
        [InlineKeyboardButton("😎 Terlalu Percaya Diri", callback_data="psy_mental_overconfident")],
        [InlineKeyboardButton("😴 Capek / Ngantuk", callback_data="psy_mental_tired")],
        [InlineKeyboardButton("❌ BATAL", callback_data="m_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def psychology_score_keyboard() -> InlineKeyboardMarkup:
    """Buttons for selecting emotion score (1-10)."""
    row1 = [InlineKeyboardButton(str(i), callback_data=f"psy_score_{i}") for i in range(1, 6)]
    row2 = [InlineKeyboardButton(str(i), callback_data=f"psy_score_{i}") for i in range(6, 11)]
    keyboard = [row1, row2, [InlineKeyboardButton("❌ BATAL", callback_data="m_main_menu")]]
    return InlineKeyboardMarkup(keyboard)

def psychology_checklist_keyboard() -> InlineKeyboardMarkup:
    """Button to confirm the discipline checklist."""
    keyboard = [
        [InlineKeyboardButton("✅ SAYA SUDAH DISIPLIN (GASS!)", callback_data="psy_checklist_ok")],
        [InlineKeyboardButton("❌ BATAL (STOP TRADE)", callback_data="m_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# =================================================================
# 9. Mentor Selection Keyboards (Post-Analysis Logic)
# =================================================================

def mentor_selection_keyboard(analysis_result: str, user_plan: str) -> InlineKeyboardMarkup:
    """
    Keyboard premium untuk memilih Mentor AI setelah hasil analisa keluar.
    """
    keyboard = []
    user_plan = user_plan.upper()
    summary_hash = hashlib.md5(analysis_result[:500].encode()).hexdigest()[:8]

    keyboard.append([
        InlineKeyboardButton("👨🏻🏫 Mentor 𝐁𝐚𝐬𝐢𝐜 (Structure Focus)", 
                             callback_data=f"mentor_basic_{summary_hash}")
    ])

    if user_plan in ['PREMIUM', 'ULTIMATE']:
        keyboard.append([
            InlineKeyboardButton("👨🏻💻 Mentor 𝐀𝐝𝐯𝐚𝐧𝐜𝐞𝐝 (SMC Specialist)", 
                                 callback_data=f"mentor_pro_{summary_hash}")
        ])

    if user_plan == 'ULTIMATE':
        keyboard.append([
            InlineKeyboardButton("🎖️ Mentor 𝐔𝐥𝐭𝐢𝐦ａ𝐭𝐞 (Risk Commander)", 
                                 callback_data=f"mentor_ss_{summary_hash}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔄 Analisa Ulang Pair Lain", callback_data="a_analisa_mandiri"),
        InlineKeyboardButton("⬅️ Markas Utama", callback_data="m_main_menu")
    ])

    return InlineKeyboardMarkup(keyboard)
