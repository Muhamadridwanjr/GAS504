from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import os

# =================================================================
# 3. Upgrade & Boost Menu Keyboards (u_)
# =================================================================

def upgrade_center_keyboard(has_active_plan: bool = False) -> InlineKeyboardMarkup:
    """Menu Utama Upgrade Center - Pembeda User Baru & Aktif."""
    keyboard = [
        [
            InlineKeyboardButton("💎 Beli PREMIUM", callback_data="u_detail_PREMIUM"),
            InlineKeyboardButton("👑 Beli ULTIMATE", callback_data="u_detail_ULTIMATE")
        ],
        [
            InlineKeyboardButton("🚀 BOOST PREMIUM", callback_data="u_boost_PREMIUM"),
            InlineKeyboardButton("🚀 BOOST ULTIMATE", callback_data="u_boost_ULTIMATE")
        ],
        [InlineKeyboardButton("📊 Bandingkan Plan PREMIUM vs ULTIMATE", callback_data="u_compare")],
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="m_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def plan_detail_keyboard(plan_name: str) -> InlineKeyboardMarkup:
    """Detail Benefit Plan & Opsi Pembayaran Crypto."""
    # Logic penentuan harga dari ENV atau Core
    price = "5.00" if plan_name == "PREMIUM" else "10.00"
    
    keyboard = [
        [InlineKeyboardButton(f"🇹💲 USDT (ERC20)", callback_data=f"p_pay_{plan_name}_ERC20")],
        [InlineKeyboardButton(f"🇹💲 USDT (TRC20)", callback_data=f"p_pay_{plan_name}_TRC20")],
        [InlineKeyboardButton(f"🇹💲 USDT (BEP20)", callback_data=f"p_pay_{plan_name}_BEP20")],
        [InlineKeyboardButton("🏛️ Bank Transfer (Soon)", callback_data="p_soon")],
        [InlineKeyboardButton("📲 E-Wallet (Soon)", callback_data="p_soon")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="u_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def payment_method_keyboard(plan_name: str) -> InlineKeyboardMarkup:
    """Tombol pilihan network USDT."""
    keyboard = [
        [InlineKeyboardButton("🇹💲 USDT (TRC20)", callback_data=f"p_method_{plan_name}_TRC20")],
        [InlineKeyboardButton("🇹💲 USDT (ERC20)", callback_data=f"p_method_{plan_name}_ERC20")],
        [InlineKeyboardButton("🇹💲 USDT (BEP20)", callback_data=f"p_method_{plan_name}_BEP20")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="u_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_payment_keyboard(invoice_id: str) -> InlineKeyboardMarkup:
    """Tombol konfirmasi setelah user melihat alamat wallet."""
    keyboard = [
        [InlineKeyboardButton("✅ SAYA SUDAH TRANSFER", callback_data=f"p_confirm_{invoice_id}")],
        [InlineKeyboardButton("⬅️ KEMBALI", callback_data="u_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def txid_input_keyboard() -> InlineKeyboardMarkup:
    """Keyboard saat user diminta input TXID."""
    keyboard = [
        [InlineKeyboardButton("⬅️ Batal & Kembali", callback_data="u_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# =====================================================================
# 🚀💎 BOOST SYSTEM KEYBOARDS
# =====================================================================

BOOST_PACKAGES = {
    "PREMIUM": {
        "header": "💎💎💎 PREMIUM BOOST\n✨ Faster • Smarter • Cheaper",
        "title": "💎 PREMIUM BOOST ($2.99/month)",
        "emoji": "🚀",
        "prefix": "u_b_prm",
        "packages": [
            {"qty": 1,  "quota": 10,  "price": 4.99,  "save": "50% OFF"},
            {"qty": 5,  "quota": 50,  "price": 12.99, "save": "57% OFF"},
            {"qty": 10, "quota": 100, "price": 39.99, "save": "60% OFF 🔥 BEST DEAL"},
        ],
    },
    "ULTIMATE": {
        "header": "👑👑👑 ULTIMATE BOOST\n⚡ Power • Priority • Maximum",
        "title": "👑 ULTIMATE BOOST ($6.99/month)",
        "emoji": "👑",
        "prefix": "u_b_ult",
        "packages": [
            {"qty": 1,  "quota": 10,  "price": 7.99,  "save": "20% OFF"},
            {"qty": 5,  "quota": 50,  "price": 21.99, "save": "26% OFF"},
            {"qty": 10, "quota": 100, "price": 59.99, "save": "40% OFF 🔥 BEST DEAL"},
        ],
    },
}

def boost_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Entry point Boost Menu
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 BOOST PREMIUM", callback_data="u_boost_PREMIUM")],
        [InlineKeyboardButton("👑 BOOST ULTIMATE", callback_data="u_boost_ULTIMATE")],
        [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="u_menu")],
    ])

def boost_packages_keyboard(plan_name: str, is_user_active: bool) -> InlineKeyboardMarkup:
    """
    Display Boost Packages based on Plan
    """
    plan_name = plan_name.upper()
    if not is_user_active:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Aktifkan PREMIUM", callback_data="u_detail_PREMIUM")],
            [InlineKeyboardButton("👑 Aktifkan ULTIMATE", callback_data="u_detail_ULTIMATE")],
            [InlineKeyboardButton("⬅️ Kembali", callback_data="u_boost_menu")],
        ])

    config = BOOST_PACKAGES.get(plan_name)
    if not config:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Kembali", callback_data="u_boost_menu")]
        ])

    keyboard = []
    keyboard.append([InlineKeyboardButton(config["header"], callback_data="noop")])
    keyboard.append([InlineKeyboardButton(config["title"], callback_data="noop")])

    for pkg in config["packages"]:
        icon = config["emoji"] * min(pkg["qty"], 3)
        text = (
            f"{icon} {pkg['qty']} Boost{'s' if pkg['qty'] > 1 else ''}\n"
            f"🎯 {pkg['quota']} Quota\n"
            f"💵 ${pkg['price']} • 🔥 {pkg['save']}"
        )
        keyboard.append([InlineKeyboardButton(text, callback_data=f"{config['prefix']}_{pkg['qty']}")])

    keyboard.append([InlineKeyboardButton("⬅️ Kembali ke Boost Menu", callback_data="u_boost_menu")])
    return InlineKeyboardMarkup(keyboard)

async def handle_boost_to_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Bridge BOOST button to existing payment engine
    """
    query = update.callback_query
    await query.answer()

    _, _, plan_short, qty = query.data.split("_")
    plan = "PREMIUM" if plan_short == "prm" else "ULTIMATE"
    callback_data = f"p_pay_BOOST_{plan}_{qty}"

    await query.message.edit_text(
        text=(
            "🚀💎 BOOST CHECKOUT\n\n"
            f"👤 Plan   : {plan}\n"
            f"⚡ Boost  : {qty}x\n\n"
            "💳 Silakan pilih metode pembayaran:"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🇹💲 USDT (TRC20)", callback_data=f"{callback_data}_TRC20")],
            [InlineKeyboardButton("🇹💲 USDT (ERC20)", callback_data=f"{callback_data}_ERC20")],
            [InlineKeyboardButton("🇹💲 USDT (BEP20)", callback_data=f"{callback_data}_BEP20")],
            [InlineKeyboardButton("⬅️ Kembali", callback_data="u_boost_menu")]
        ])
    )
