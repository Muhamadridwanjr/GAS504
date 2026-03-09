import os
import hashlib
from typing import Dict, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes

# =================================================================
# 1. Start & Trial Menu Keyboards (s_)
# =================================================================

def start_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard untuk menu /start."""
    keyboard = [
        [InlineKeyboardButton("🧠 Inisialisasi Profil Trading", callback_data="i_step_0")],
        [InlineKeyboardButton("🎁 Ambil 1x Kuota Trial Gratis", callback_data="s_trial_start")],
        [InlineKeyboardButton("🚀 Upgrade ke Premium/Ultimate", callback_data="u_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def trial_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard Trial - Terbatas 1 kuota sesuai SOP."""
    keyboard = [
        [InlineKeyboardButton("⚡ Jalankan 1x Analisis Trial 🅱️", callback_data="s_run_trial_ta_b")],
        [InlineKeyboardButton("🚀 Upgrade ke Premium/Ultimate", callback_data="u_menu")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="m_main_menu")],
    ]
    # Catatan: User hanya punya 1 kesempatan eksekusi di sini.
    return InlineKeyboardMarkup(keyboard)
