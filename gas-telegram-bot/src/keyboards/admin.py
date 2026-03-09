from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# =================================================================
# 1. Admin Verification Keyboards (Manual Check)
# =================================================================

def admin_verify_keyboard(user_id: str, invoice_id: str = "N/A", network: str = "TRC20", full_txid: str = "") -> InlineKeyboardMarkup:
    """
    Keyboard Admin dengan optimasi panjang data untuk mencegah 'Button_data_invalid'.
    """
    tx_link = full_txid if full_txid else invoice_id
    
    if network == "TRC20":
        scan_url = f"https://tronscan.org/#/transaction/{tx_link}"
    elif network in ["ERC20", "ETH"]:
        scan_url = f"https://etherscan.io/tx/{tx_link}"
    elif network in ["BSC", "BEP20"]:
        scan_url = f"https://bscscan.com/tx/{tx_link}"
    else:
        scan_url = f"https://google.com/search?q=blockchain+explorer+{tx_link}"

    keyboard = [
        [InlineKeyboardButton("🔍 Cek di Blockchain Explorer", url=scan_url)],
        [
            InlineKeyboardButton("✅ AKTIVASI", callback_data=f"adm_app_{user_id}_{invoice_id}"),
            InlineKeyboardButton("❌ TOLAK", callback_data=f"adm_rej_{user_id}_{invoice_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

admin_approve_keyboard = admin_verify_keyboard

def failed_verification_retry_keyboard() -> InlineKeyboardMarkup:
    """Keyboard jika verifikasi gagal."""
    keyboard = [
        [InlineKeyboardButton("🔄 Input Ulang TXID", callback_data="p_retry_txid")],
        [InlineKeyboardButton("📞 Hubungi Admin", url="https://t.me/mr7wanjroke")],
        [InlineKeyboardButton("🏠 Menu Utama", callback_data="m_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
