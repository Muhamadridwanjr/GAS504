from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# =================================================================
# 7. Inisialisasi Profil Keyboards (i_) - ULTIMATE 30-STEPS
# =================================================================

def step_header(title: str, subtitle: str) -> list:
    return [[InlineKeyboardButton(f"{title}\n{subtitle}", callback_data="noop")]]

def init_step_keyboard(step: int) -> InlineKeyboardMarkup:
    keyboard = []
    
    # Pre-calculated data for steps to keep it clean
    step_data = {
        0: ("🚀 AKTIVASI PROFIL TEMPUR", "Inisialisasi DNA Trading Anda (30-Step System)", [("🔥 MULAI SEKARANG", "i_step_1")]),
        1: ("🧭 STEP 1 — PENGALAMAN TRADING", "Menentukan level kematangan & ekspektasi strategi", [("🌱 Newbie (0–3 Bulan)", "i_select_1_newbie"), ("📚 Learner (3–9 Bulan)", "i_select_1_learner"), ("🔥 Intermediate (1–3 Tahun)", "i_select_1_inter"), ("⚡ Advanced (3–7 Tahun)", "i_select_1_adv"), ("🏆 Elite / Funded", "i_select_1_elite"), ("✍️ Custom Input", "i_custom_1")]),
        2: ("🏦 STEP 2 — TIPE AKUN TRADING", "Lingkungan akun menentukan agresivitas & rule set", [("🏦 Retail Standard", "i_select_2_standard"), ("💎 Retail ECN / Raw", "i_select_2_ecn"), ("🚀 Prop Firm Challenge", "i_select_2_prop"), ("🏢 Proprietary Trading", "i_select_2_private"), ("🧪 Demo / Paper", "i_select_2_demo"), ("✍️ Custom Input", "i_custom_2")]),
        3: ("💼 STEP 3 — SUMBER MODAL", "Asal modal memengaruhi psikologi & risk tolerance", [("💰 Personal Savings", "i_select_3_personal"), ("🏢 Business Revenue", "i_select_3_business"), ("🤝 Partnership Money", "i_select_3_partner"), ("🚀 Prop Firm Capital", "i_select_3_prop"), ("✍️ Custom Input", "i_custom_3")]),
        4: ("📱 STEP 4 — PLATFORM UTAMA", "Platform menentukan eksekusi & integrasi AI", [("📱 MT4", "i_select_4_mt4"), ("📊 MT5", "i_select_4_mt5"), ("🌐 TradingView + Broker", "i_select_4_tv"), ("💻 cTrader", "i_select_4_ctrader"), ("✍️ Custom Input", "i_custom_4")]),
        5: ("⚙️ STEP 5 — SETUP TEKNIS", "Perangkat = kecepatan, fokus, dan presisi", [("🖥️ PC Multi Monitor", "i_select_5_pc"), ("💻 Laptop + Mobile", "i_select_5_laptop"), ("☁️ VPS / Cloud Trading", "i_select_5_vps"), ("🏢 Trading Room", "i_select_5_room"), ("✍️ Custom Input", "i_custom_5")]),
        6: ("⏰ STEP 6 — WAKTU TRADING", "Durasi harian menentukan style & fatigue control", [("⏰ 1–2 Jam", "i_select_6_1_2"), ("⏰ 3–4 Jam", "i_select_6_3_4"), ("⏰ 5–8 Jam", "i_select_6_5_8"), ("🌙 24/5 Session", "i_select_6_full"), ("✍️ Custom Input", "i_custom_6")]),
        7: ("🎯 STEP 7 — TUJUAN FINANSIAL", "Tujuan = arah keputusan & disiplin jangka panjang", [("🎯 Extra Income", "i_select_7_extra"), ("🚀 Replace Job", "i_select_7_replace"), ("🏦 Wealth Building", "i_select_7_wealth"), ("🏆 Legacy Creation", "i_select_7_legacy"), ("✍️ Custom Input", "i_custom_7")]),
        8: ("⚡ STEP 8 — STYLE TRADING", "Menentukan ritme, frekuensi, dan tekanan psikologis", [("⚡ Pure Scalping (1–5M)", "i_select_8_scalp"), ("📈 Intraday (15M–1H)", "i_select_8_intraday"), ("🌙 Swing (H4–D1)", "i_select_8_swing"), ("⏳ Position (D1–W1)", "i_select_8_position"), ("🤖 Algo / EA", "i_select_8_algo"), ("✍️ Custom", "i_custom_8")]),
        9: ("🔧 STEP 9 — METODOLOGI ANALISIS", "Kerangka berpikir utama dalam membaca market", [("📊 Price Action", "i_select_9_pa"), ("📈 Indicators", "i_select_9_indicator"), ("🏗️ SMC / ICT", "i_select_9_smc"), ("🎯 Fibonacci / Harmonic", "i_select_9_fibo"), ("🤖 Quant / Data", "i_select_9_quant"), ("✍️ Custom", "i_custom_9")]),
        10: ("🟡 STEP 10 — PASAR UTAMA", "Menentukan karakter volatilitas & likuiditas", [("🟡 XAUUSD (Gold)", "i_select_10_gold"), ("💵 Forex Majors", "i_select_10_fx"), ("📈 US Indices", "i_select_10_indices"), ("🟠 Cryptocurrency", "i_select_10_crypto"), ("🛢️ Energy Commodities", "i_select_10_energy"), ("✍️ Custom", "i_custom_10")]),
        11: ("🎯 STEP 11 — INSTRUMEN SPESIFIK", "Fokus instrumen = fokus edge", [("🎯 EURUSD + Gold", "i_select_11_eu_gold"), ("📈 NAS100 + Tech", "i_select_11_nas"), ("🟠 BTC + Altcoins", "i_select_11_crypto"), ("🛢️ Oil & Gas", "i_select_11_energy"), ("🌍 Multi Instrument", "i_select_11_multi"), ("✍️ Custom", "i_custom_11")]),
        12: ("⏱️ STEP 12 — TIMEFRAME", "Menentukan sudut pandang & holding time", [("⚡ M1–M5", "i_select_12_micro"), ("📈 M15–H1", "i_select_12_intraday"), ("🌙 H4–D1", "i_select_12_swing"), ("⏳ W1–MN", "i_select_12_position"), ("🎯 Multi-TF", "i_select_12_multi"), ("✍️ Custom", "i_custom_12")]),
        13: ("🏗️ STEP 13 — ENTRY CONFIRMATION", "Syarat valid sebelum eksekusi", [("🏗️ BOS / CHoCH + Liquidity", "i_select_13_bos"), ("📦 Order Block + FVG", "i_select_13_ob"), ("🕯️ Candlestick Pattern", "i_select_13_candle"), ("📊 Indicator Confluence", "i_select_13_indicator"), ("🌊 Market Structure Break", "i_select_13_structure"), ("✍️ Custom", "i_custom_13")]),
        14: ("🎭 STEP 14 — STYLE PSIKOLOGIS", "Bagaimana Anda mengeksekusi tekanan", [("🎭 Disciplined Executor", "i_select_14_disciplined"), ("🔥 Aggressive Hunter", "i_select_14_aggressive"), ("🎯 Patient Sniper", "i_select_14_sniper"), ("⚖️ Calculated Risk Taker", "i_select_14_calculated"), ("🧠 Adaptive Trader", "i_select_14_adaptive"), ("✍️ Custom", "i_custom_14")]),
        15: ("💰 STEP 15 — MODAL TRADING", "Ukuran amunisi menentukan gaya serang & kontrol risiko", [("💰 $100 – $500", "i_select_15_100_500"), ("💰 $501 – $2,000", "i_select_15_501_2000"), ("💰 $2,001 – $10,000", "i_select_15_2001_10000"), ("💰 $10,001 – $50,000", "i_select_15_10001_50000"), ("🐋 $50,001+", "i_select_15_whale"), ("✍️ Custom Modal", "i_custom_15")]),
        16: ("⚖️ STEP 16 — LEVERAGE", "Pengganda kekuatan sekaligus sumber kehancuran", [("🛡️ 1:10 (Ultra Safe)", "i_select_16_10"), ("⚖️ 1:30 (Conservative)", "i_select_16_30"), ("📊 1:100 (Standard)", "i_select_16_100"), ("🔥 1:200 (Aggressive)", "i_select_16_200"), ("🚀 1:500+ (Maximum)", "i_select_16_500"), ("✍️ Custom Leverage", "i_custom_16")]),
        17: ("🛡️ STEP 17 — RISK PER TRADE", "Satu peluru, satu keputusan", [("🧊 0.1% (Very Safe)", "i_select_17_01"), ("🛡️ 0.25% (Conservative)", "i_select_17_025"), ("⚖️ 0.5% (Moderate)", "i_select_17_05"), ("🔥 1.0% (Standard)", "i_select_17_1"), ("💀 2.0%+ (Aggressive)", "i_select_17_2"), ("✍️ Custom Risk", "i_custom_17")]),
        18: ("🛑 STEP 18 — MAX DAILY LOSS", "Batas kerusakan sebelum sistem mengunci senjata", [("🧊 1% (Ultra Safe)", "i_select_18_1"), ("🛡️ 2% (Conservative)", "i_select_18_2"), ("⚖️ 3% (Standard)", "i_select_18_3"), ("🔥 5% (Aggressive)", "i_select_18_5"), ("💀 10%+ (High Risk)", "i_select_18_10"), ("✍️ Custom Limit", "i_custom_18")]),
        19: ("🗳️ STEP 19 — MAKSIMAL POSISI AKTIF", "Kontrol exposure & chaos simultan", [("🗳️ 1 Trade Only", "i_select_19_1"), ("🗳️ 2–3 Trades", "i_select_19_2_3"), ("🗳️ 4–5 Trades", "i_select_19_4_5"), ("🌀 6–10 Trades", "i_select_19_6_10"), ("🔥 10+ Trades", "i_select_19_10_plus"), ("✍️ Custom Count", "i_custom_19")]),
        20: ("🎯 STEP 20 — TARGET RISK / REWARD", "Rasio kemenangan jangka panjang", [("🎯 1:1 (Scalping)", "i_select_20_1_1"), ("⚖️ 1:1.5 (Balanced)", "i_select_20_1_15"), ("📈 1:2 (Optimal)", "i_select_20_1_2"), ("🏆 1:3 (Professional)", "i_select_20_1_3"), ("🎯 1:5+ (Sniper)", "i_select_20_1_5"), ("✍️ Custom R:R", "i_custom_20")]),
        21: ("📏 STEP 21 — STOP LOSS METHOD", "Garis terakhir antara disiplin dan kehancuran", [("🏗️ Structure Break", "i_select_21_structure"), ("📦 Fixed Pips (10–30)", "i_select_21_fixed"), ("🌪️ ATR Based", "i_select_21_atr"), ("📉 % of Account", "i_select_21_percent"), ("🧠 Mental Stop", "i_select_21_mental"), ("✍️ Custom SL", "i_custom_21")]),
        22: ("🏁 STEP 22 — TAKE PROFIT STRATEGY", "Cara Anda mengamankan kemenangan", [("🏁 Single TP (Hit & Run)", "i_select_22_single"), ("🎯 Multiple TP (Scale Out)", "i_select_22_multi"), ("🏃 Trailing Stop", "i_select_22_trailing"), ("⏱️ Time-Based Exit", "i_select_22_time"), ("📊 Price Action Exit", "i_select_22_pa"), ("✍️ Custom TP", "i_custom_22")]),
        23: ("📻 STEP 23 — NEWS APPROACH", "Reaksi Anda terhadap ledakan volatilitas", [("🚫 Avoid News (±30m)", "i_select_23_avoid"), ("⚖️ Reduce Lot 50%", "i_select_23_reduce"), ("🔥 Trade Through News", "i_select_23_through"), ("🛡️ Hedge Positions", "i_select_23_hedge"), ("📅 Calendar Only", "i_select_23_calendar"), ("✍️ Custom News Rule", "i_custom_23")]),
        24: ("🌍 STEP 24 — SESSION PREFERENCE", "Zona waktu favorit tempat Anda berburu peluang", [("🌏 Asia Session", "i_select_24_asia"), ("🔵 London Session", "i_select_24_london"), ("🗽 New York Session", "i_select_24_ny"), ("⚡ London–NY Overlap", "i_select_24_overlap"), ("🌙 24/5 Market", "i_select_24_full"), ("✍️ Custom Session", "i_custom_24")]),
        25: ("📈 STEP 25 — WIN / LOSS RESPONSE", "Apa yang Anda lakukan setelah hasil keluar", [("🛑 Take 1 Day Off", "i_select_25_off"), ("⚖️ Reduce Size 50%", "i_select_25_reduce"), ("➡️ Continue Normal", "i_select_25_continue"), ("🔍 Increase Analysis", "i_select_25_analyze"), ("📊 Review Strategy", "i_select_25_review"), ("✍️ Custom Response", "i_custom_25")]),
        26: ("📉 STEP 26 — DRAWDOWN RESPONSE", "Respons Anda saat sistem berada di zona kritis", [("🛑 Stop 1 Minggu", "i_select_26_stop_week"), ("⚖️ Halve Position Size", "i_select_26_half"), ("🧊 Continue with Caution", "i_select_26_caution"), ("🔍 Strategy Review", "i_select_26_review"), ("🧠 Mental Reset", "i_select_26_reset"), ("✍️ Custom Response", "i_custom_26")]),
        27: ("📚 STEP 27 — LEARNING METHOD", "Bagaimana Anda meng-upgrade skill & edge", [("🎥 YouTube + Courses", "i_select_27_video"), ("📖 Books + Journals", "i_select_27_books"), ("👥 Mentor / Community", "i_select_27_mentor"), ("🧪 Backtesting", "i_select_27_backtest"), ("🔥 Live Experience", "i_select_27_live"), ("✍️ Custom Method", "i_custom_27")]),
        28: ("🧘 STEP 28 — PRE-TRADE RITUAL", "Ritual sebelum masuk medan perang", [("🧘 Meditation / Breathing", "i_select_28_meditation"), ("📊 Market Scan", "i_select_28_scan"), ("📝 Plan Review", "i_select_28_plan"), ("☕ Coffee + Focus", "i_select_28_coffee"), ("🎮 Warm-Up Routine", "i_select_28_warmup"), ("✍️ Custom Ritual", "i_custom_28")]),
        29: ("🤖 STEP 29 — AUTOMATION LEVEL", "Seberapa besar Anda mempercayakan eksekusi ke sistem", [("✋ Fully Manual", "i_select_29_manual"), ("🔔 Alerts + Manual Entry", "i_select_29_alert"), ("🤖 Semi-Auto (Signals)", "i_select_29_semi"), ("⚙️ Full Auto (EA)", "i_select_29_auto"), ("🧠 AI-Driven Trading", "i_select_29_ai"), ("✍️ Custom Level", "i_custom_29")]),
        30: ("🏆 STEP 30 — DEFINISI KESUKSESAN", "Standar akhir yang menentukan status Anda", [("🏆 Konsistensi 80%+", "i_select_30_consistency"), ("📈 Profit Factor > 1.5", "i_select_30_pf"), ("🛡️ Max Drawdown < 10%", "i_select_30_dd"), ("💰 Monthly Return 5%+", "i_select_30_monthly"), ("🎯 Risk/Reward 1:2+", "i_select_30_rr"), ("✅ AKTIFKAN PROFIL SAYA", "i_confirm_activate")])
    }
    
    if step in step_data:
        title, subtitle, buttons = step_data[step]
        keyboard = [*step_header(title, subtitle)]
        # Split buttons into rows of 2 if there are many
        for i in range(0, len(buttons), 2):
            row = [InlineKeyboardButton(text, callback_data=data) for text, data in buttons[i:i+2]]
            keyboard.append(row)
            
    if 1 < step <= 30:
        keyboard.append([InlineKeyboardButton("⬅️ Langkah Sebelumnya", callback_data=f"i_step_{step-1}")])
        
    return InlineKeyboardMarkup(keyboard)

def init_success_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🛒 Akses Premium Plan", callback_data="u_menu")],
        [InlineKeyboardButton("📊 Mulai Analisa Mandiri", callback_data="a_analisa_mandiri")],
        [InlineKeyboardButton("👤 Lihat Profil Trading Saya", callback_data="i_view_profile")],
        [InlineKeyboardButton("⬅️ Kembali ke Markas Utama", callback_data="m_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
