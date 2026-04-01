"""
GAS Bot — Market & Pair Keyboards (plan-aware)
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.config import get_plan_cfg


# ── Plan-filtered helpers ──────────────────────────────────────────────────────

def _cat_label_with_lock(cat: str, allowed_cats: set) -> str:
    labels = {
        "FOREX": "💱 Forex", "CRYPTO": "₿ Crypto",
        "COMMODITY": "🥇 Komoditas", "INDEX": "📈 Indeks",
        "MEME": "🐸 Meme Coins", "STOCK": "💻 Saham US",
    }
    base = labels.get(cat, cat)
    return base if cat in allowed_cats else f"🔒 {base}"


# ── Market Category ───────────────────────────────────────────────────────────

def market_category_keyboard(flow_type: str = "analysis", plan: str = "free") -> InlineKeyboardMarkup:
    cfg = get_plan_cfg(plan)
    allowed = cfg["cats"]

    def _btn(cat: str) -> InlineKeyboardButton:
        label = _cat_label_with_lock(cat, allowed)
        # locked cats still show but callback tells handler to gate
        return InlineKeyboardButton(label, callback_data=f"mkt_cat_{cat}_{flow_type}")

    return InlineKeyboardMarkup([
        [_btn("FOREX"),     _btn("CRYPTO")],
        [_btn("COMMODITY"), _btn("INDEX")],
        [_btn("MEME"),      _btn("STOCK")],
        [InlineKeyboardButton("🎲 Polymarket", callback_data="mkt_polymarket")],
        [InlineKeyboardButton("🏠 Menu Utama", callback_data="m_main_menu")],
    ])


# ── Pair Lists ─────────────────────────────────────────────────────────────────

FOREX_PAIRS = [
    # Major Pairs ── live data confirmed in Redis
    ("XAUUSD",  "🥇 XAU/USD  (Gold)"),
    ("EURUSD",  "💶 EUR/USD"),
    ("GBPUSD",  "💷 GBP/USD"),
    ("USDJPY",  "¥  USD/JPY"),
    ("AUDUSD",  "🦘 AUD/USD"),
    ("USDCAD",  "🍁 USD/CAD"),
    ("NZDUSD",  "🥝 NZD/USD"),
    ("USDCHF",  "🇨🇭 USD/CHF"),
    # Cross Pairs
    ("GBPJPY",  "💷 GBP/JPY"),
    ("EURJPY",  "💶 EUR/JPY"),
    ("EURGBP",  "💶 EUR/GBP"),
    ("AUDJPY",  "🦘 AUD/JPY"),
    ("CADJPY",  "🍁 CAD/JPY"),
    ("GBPCAD",  "💷 GBP/CAD"),
    # Exotic
    ("USDCNH",  "🇨🇳 USD/CNH"),
    ("USDSEK",  "🇸🇪 USD/SEK"),
]

CRYPTO_PAIRS = [
    # Large Cap
    ("BTCUSD",   "₿  BTC/USD"),
    ("ETHUSD",   "⬡  ETH/USD"),
    ("BNBUSDT",  "🔶 BNB/USDT"),
    ("SOLUSDT",  "◎  SOL/USDT"),
    ("XRPUSDT",  "✦  XRP/USDT"),
    ("ADAUSDT",  "🔵 ADA/USDT"),
    # Mid Cap
    ("AVAXUSDT", "🔺 AVAX/USDT"),
    ("DOTUSDT",  "⚪ DOT/USDT"),
    ("LINKUSDT", "🔗 LINK/USDT"),
    ("LTCUSDT",  "🥈 LTC/USDT"),
    ("MATICUSDT","🟣 MATIC/USDT"),
    ("TONUSDT",  "💎 TON/USDT"),
]

COMMODITY_PAIRS = [
    ("XAUUSD",  "🥇 Gold / XAU"),
    ("XAGUSD",  "🥈 Silver / XAG"),
    ("USOIL",   "🛢️ WTI Crude Oil"),
    ("UKOIL",   "🛢️ Brent Crude"),
    ("NATGAS",  "🔥 Natural Gas"),
    ("COPPER",  "🟤 Copper"),
    ("WHEAT",   "🌾 Wheat"),
    ("CORN",    "🌽 Corn"),
]

INDEX_PAIRS = [
    ("US30",   "🏛  Dow Jones 30"),
    ("US500",  "📊 S&P 500"),
    ("USTEC",  "💻 Nasdaq 100"),
    ("GER40",  "🇩🇪 DAX 40"),
    ("JPN225", "🇯🇵 Nikkei 225"),
    ("UK100",  "🇬🇧 FTSE 100"),
    ("AUS200", "🇦🇺 ASX 200"),
    ("FRA40",  "🇫🇷 CAC 40"),
    ("ESP35",  "🇪🇸 IBEX 35"),
    ("HK50",   "🇭🇰 Hang Seng"),
]

MEME_PAIRS = [
    ("DOGEUSDT",  "🐶 DOGE/USDT"),
    ("SHIBUSDT",  "🦊 SHIB/USDT"),
    ("PEPEUSDT",  "🐸 PEPE/USDT"),
    ("WIFUSDT",   "🐕 WIF/USDT"),
    ("BONKUSDT",  "🔔 BONK/USDT"),
    ("FLOKIUSDT", "⚡ FLOKI/USDT"),
    ("MOGUSDT",   "😼 MOG/USDT"),
    ("BRETTUSDT", "🟦 BRETT/USDT"),
    ("POPCATUSDT","🐱 POPCAT/USDT"),
    ("MEWUSDT",   "🐈 MEW/USDT"),
]

STOCK_PAIRS = [
    # Live data confirmed in Redis
    ("NVDA",  "🟢 NVDA (Nvidia)"),
    ("MSFT",  "🔵 MSFT (Microsoft)"),
    ("AMD",   "🔴 AMD"),
    ("INTC",  "🔵 INTC (Intel)"),
    # Major US Stocks
    ("AAPL",  "🍎 AAPL (Apple)"),
    ("TSLA",  "⚡ TSLA (Tesla)"),
    ("AMZN",  "📦 AMZN (Amazon)"),
    ("GOOGL", "🔍 GOOGL (Google)"),
    ("META",  "👓 META"),
    ("COIN",  "₿  COIN (Coinbase)"),
]

# Featured pair shown in Signal flow (fast — no pair picker)
FEATURED_PAIR = {
    "FOREX":     "XAUUSD",
    "CRYPTO":    "BTCUSD",
    "COMMODITY": "XAUUSD",
    "INDEX":     "US30",
    "MEME":      "DOGEUSDT",
    "STOCK":     "NVDA",
}

_CAT_PAIRS = {
    "FOREX":     FOREX_PAIRS,
    "CRYPTO":    CRYPTO_PAIRS,
    "COMMODITY": COMMODITY_PAIRS,
    "INDEX":     INDEX_PAIRS,
    "MEME":      MEME_PAIRS,
    "STOCK":     STOCK_PAIRS,
}

CAT_LABELS = {
    "FOREX":     "💱 Forex",
    "CRYPTO":    "₿ Crypto",
    "COMMODITY": "🥇 Komoditas",
    "INDEX":     "📈 Indeks",
    "MEME":      "🐸 Meme Coins",
    "STOCK":     "💻 Saham US",
}


def _pair_keyboard(pairs: list, flow_type: str, limit_pairs: set = None) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for sym, label in pairs:
        locked = limit_pairs is not None and sym not in limit_pairs
        btn_label = f"🔒 {label}" if locked else label
        row.append(InlineKeyboardButton(btn_label, callback_data=f"mkt_pair_{sym}_{flow_type}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Pilih Market", callback_data=f"nav_market_{flow_type}")])
    return InlineKeyboardMarkup(buttons)


def pair_keyboard_for_plan(cat: str, flow_type: str, plan: str = "free") -> InlineKeyboardMarkup:
    """Return pair keyboard filtered/locked by plan."""
    cfg = get_plan_cfg(plan)
    pairs = _CAT_PAIRS.get(cat, [])
    return _pair_keyboard(pairs, flow_type, limit_pairs=cfg.get("limit_pairs"))


def forex_market_keyboard(flow_type: str = "analysis") -> InlineKeyboardMarkup:
    return _pair_keyboard(FOREX_PAIRS, flow_type)

def crypto_market_keyboard(flow_type: str = "analysis") -> InlineKeyboardMarkup:
    return _pair_keyboard(CRYPTO_PAIRS, flow_type)

def commodity_market_keyboard(flow_type: str = "analysis") -> InlineKeyboardMarkup:
    return _pair_keyboard(COMMODITY_PAIRS, flow_type)

def index_market_keyboard(flow_type: str = "analysis") -> InlineKeyboardMarkup:
    return _pair_keyboard(INDEX_PAIRS, flow_type)

def meme_market_keyboard(flow_type: str = "analysis") -> InlineKeyboardMarkup:
    return _pair_keyboard(MEME_PAIRS, flow_type)

def stock_market_keyboard(flow_type: str = "analysis") -> InlineKeyboardMarkup:
    return _pair_keyboard(STOCK_PAIRS, flow_type)


CAT_KEYBOARDS = {
    "FOREX":     forex_market_keyboard,
    "CRYPTO":    crypto_market_keyboard,
    "COMMODITY": commodity_market_keyboard,
    "INDEX":     index_market_keyboard,
    "MEME":      meme_market_keyboard,
    "STOCK":     stock_market_keyboard,
}


# ── Polymarket ─────────────────────────────────────────────────────────────────

def polymarket_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("₿ BTC >$100k Q2 2025?",      callback_data="poly_btc100k")],
        [InlineKeyboardButton("⬡ ETH >$5k in 2025?",         callback_data="poly_eth5k")],
        [InlineKeyboardButton("🏛 Fed Rate Cut March 2025?", callback_data="poly_fedcut")],
        [InlineKeyboardButton("📉 US Recession 2025?",        callback_data="poly_recession")],
        [InlineKeyboardButton("🌐 Buka Polymarket.com",       url="https://polymarket.com")],
        [InlineKeyboardButton("🔙 News",                      callback_data="m_news"),
         InlineKeyboardButton("🏠 Menu Utama",                callback_data="m_main_menu")],
    ])
