from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# =================================================================
# 6. AI Analyst Menu Keyboards (v3.1 - Refined Tier & Full Pairs)
# =================================================================

def golden_ai_strategy_menu_keyboard(user_plan: str = "FREE") -> InlineKeyboardMarkup:
    """Menu Utama berdasarkan Tier."""
    user_plan = user_plan.upper()
    if user_plan == "ULTIMATE":
        return ultimate_user_keyboard()
    elif user_plan == "PREMIUM":
        return premium_user_keyboard()
    else:
        keyboard = [
            [InlineKeyboardButton("📊 Analisa Mandiri", callback_data="a_analisa_mandiri")],
            [InlineKeyboardButton("🚀 UPGRADE KE PREMIUM", callback_data="m_buy_premium")],
            [InlineKeyboardButton("⬅️ Menu Utama", callback_data="m_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

def premium_user_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🚀 Beli BOOST PREMIUM", callback_data="m_buy_boost_premium")],
        [InlineKeyboardButton("📊 Analisa Mandiri", callback_data="a_analisa_mandiri")],
        [InlineKeyboardButton("⬅️ Menu Utama", callback_data="m_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def ultimate_user_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🚀 Beli BOOST ULTIMATE", callback_data="m_buy_boost_ultimate")],
        [InlineKeyboardButton("📊 Analisa Mandiri", callback_data="a_analisa_mandiri")],
        [InlineKeyboardButton("🔴 Live Trade Tracking", callback_data="a_live_trade_track")],
        [InlineKeyboardButton("🔴 Live Market FX", callback_data="a_live_market_fx")],
        [InlineKeyboardButton("🔴 Live Trade Signal", callback_data="a_live_signal")],
        [InlineKeyboardButton("👨🏻💻 EA Monitoring", callback_data="ea_monitoring")],
        [InlineKeyboardButton("👨🏻💻 EA Executor", callback_data="ea_executor")],
        [InlineKeyboardButton("👨🏻💻 EA GAS ADVANCE", callback_data="ea_gas_advance")],
        [InlineKeyboardButton("⬅️ Menu Utama", callback_data="m_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def ai_analysis_method_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🤖 AI Technical Analysis", callback_data="a_method_TECH")],
        [InlineKeyboardButton("🤖 AI Fundamental Analysis", callback_data="a_method_FUND")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="a_back_to_tier_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def ai_instrument_category_keyboard(method: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("💱 FOREX", callback_data=f"instr_{method}_FOREX"),
         InlineKeyboardButton("🪙 CRYPTO", callback_data=f"instr_{method}_CRYPTO")],
        [InlineKeyboardButton("🛢️ COMMODITY", callback_data=f"instr_{method}_COMMODITY"),
         InlineKeyboardButton("📈 STOCKS", callback_data=f"instr_{method}_STOCKS")],
        [InlineKeyboardButton("📊 INDEX", callback_data=f"instr_{method}_INDEX"),
         InlineKeyboardButton("📜 BOND", callback_data=f"instr_{method}_BOND")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="a_analisa_mandiri")]
    ]
    return InlineKeyboardMarkup(keyboard)

def forex_pairs_keyboard(method: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🏛️ MAJORS (Top 10)", callback_data="label")],
        [InlineKeyboardButton("🇪🇺 EURUSD", callback_data=f"p_{method}_EURUSD"), InlineKeyboardButton("🇯🇵 USDJPY", callback_data=f"p_{method}_USDJPY")],
        [InlineKeyboardButton("🇬🇧 GBPUSD", callback_data=f"p_{method}_GBPUSD"), InlineKeyboardButton("🇦🇺 AUDUSD", callback_data=f"p_{method}_AUDUSD")],
        [InlineKeyboardButton("🇨🇦 USDCAD", callback_data=f"p_{method}_USDCAD"), InlineKeyboardButton("🇨🇭 USDCHF", callback_data=f"p_{method}_USDCHF")],
        [InlineKeyboardButton("🇳🇿 NZDUSD", callback_data=f"p_{method}_NZDUSD"), InlineKeyboardButton("🇪🇺🇯🇵 EURJPY", callback_data=f"p_{method}_EURJPY")],
        [InlineKeyboardButton("🇬🇧🇯🇵 GBPJPY", callback_data=f"p_{method}_GBPJPY"), InlineKeyboardButton("🇪🇺🇬🇧 EURGBP", callback_data=f"p_{method}_EURGBP")],
        
        [InlineKeyboardButton("📉 MINORS & CROSSES (Top 10)", callback_data="label")],
        [InlineKeyboardButton("🇪🇺🇦🇺 EURAUD", callback_data=f"p_{method}_EURAUD"), InlineKeyboardButton("🇬🇧🇦🇺 GBPAUD", callback_data=f"p_{method}_GBPAUD")],
        [InlineKeyboardButton("🇪🇺🇨🇦 EURCAD", callback_data=f"p_{method}_EURCAD"), InlineKeyboardButton("🇬🇧🇨🇦 GBPCAD", callback_data=f"p_{method}_GBPCAD")],
        [InlineKeyboardButton("🇦🇺🇯🇵 AUDJPY", callback_data=f"p_{method}_AUDJPY"), InlineKeyboardButton("🇨🇦🇯🇵 CADJPY", callback_data=f"p_{method}_CADJPY")],
        [InlineKeyboardButton("🇳🇿🇯🇵 NZDJPY", callback_data=f"p_{method}_NZDJPY"), InlineKeyboardButton("🇨🇭🇯🇵 CHFJPY", callback_data=f"p_{method}_CHFJPY")],
        [InlineKeyboardButton("🇦🇺🇳🇿 AUDNZD", callback_data=f"p_{method}_AUDNZD"), InlineKeyboardButton("🇪🇺🇨🇭 EURCHF", callback_data=f"p_{method}_EURCHF")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data=f"a_method_{method}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def crypto_pairs_keyboard(method: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🪙 CRYPTO MAJORS (Top 10)", callback_data="label")],
        [InlineKeyboardButton("🟠 BTCUSDT", callback_data=f"p_{method}_BTCUSDT"), InlineKeyboardButton("🔹 ETHUSDT", callback_data=f"p_{method}_ETHUSDT")],
        [InlineKeyboardButton("☀️ SOLUSDT", callback_data=f"p_{method}_SOLUSDT"), InlineKeyboardButton("🟡 BNBUSDT", callback_data=f"p_{method}_BNBUSDT")],
        [InlineKeyboardButton("📈 XRPUSDT", callback_data=f"p_{method}_XRPUSDT"), InlineKeyboardButton("🔵 ADAUSDT", callback_data=f"p_{method}_ADAUSDT")],
        [InlineKeyboardButton("🟣 DOTUSDT", callback_data=f"p_{method}_DOTUSDT"), InlineKeyboardButton("🔗 LINKUSDT", callback_data=f"p_{method}_LINKUSDT")],
        [InlineKeyboardButton("💎 AVAXUSDT", callback_data=f"p_{method}_AVAXUSDT"), InlineKeyboardButton("🐕 DOGEUSDT", callback_data=f"p_{method}_DOGEUSDT")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data=f"a_method_{method}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def commodity_pairs_keyboard(method: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("✨ METALS & ENERGY (Top 10)", callback_data="label")],
        [InlineKeyboardButton("🟡 XAUUSD", callback_data=f"p_{method}_XAUUSD"), InlineKeyboardButton("⚪ XAGUSD", callback_data=f"p_{method}_XAGUSD")],
        [InlineKeyboardButton("🛢️ WTI OIL", callback_data=f"p_{method}_WTI"), InlineKeyboardButton("🌊 BRENT", callback_data=f"p_{method}_BRENT")],
        [InlineKeyboardButton("🔥 NATGAS", callback_data=f"p_{method}_NATGAS"), InlineKeyboardButton("🥉 COPPER", callback_data=f"p_{method}_COPPER")],
        [InlineKeyboardButton("💍 PLATINUM", callback_data=f"p_{method}_PLATINUM"), InlineKeyboardButton("💿 PALLADIUM", callback_data=f"p_{method}_PALLADIUM")],
        [InlineKeyboardButton("🌽 CORN", callback_data=f"p_{method}_CORN"), InlineKeyboardButton("☕ COFFEE", callback_data=f"p_{method}_COFFEE")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data=f"a_method_{method}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def trading_style_keyboard(method: str, pair: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("⚡ SCALPING (M1, M5, M15, H1)", callback_data=f"exec_{method}_{pair}_SCALPING")],
        [InlineKeyboardButton("🕯️ INTRADAY (M15, H1, H4, D1)", callback_data=f"exec_{method}_{pair}_INTRADAY")],
        [InlineKeyboardButton("🌊 SWING (H1, H4, D1, W1)", callback_data=f"exec_{method}_{pair}_SWING")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data=f"instr_{method}_BACK")]
    ]
    return InlineKeyboardMarkup(keyboard)
