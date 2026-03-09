from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from src.keyboards import start_menu_keyboard, trial_menu_keyboard, main_menu_keyboard
from src.utils.logger import logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    user = update.effective_user
    logger.info("command_start", user_id=user.id)
    
    await update.message.reply_text(
        f"Halo {user.first_name}! Selamat datang di Golden AI Strategy (GAS) Bot.\n\n"
        "Silakan pilih menu di bawah ini untuk memulai:",
        reply_markup=start_menu_keyboard()
    )
    # Also send reply keyboard for main menu
    await update.message.reply_text(
        "Dashboard GAS Bot Aktif.",
        reply_markup=main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /help command."""
    await update.message.reply_text("Bantuan sedang disiapkan. Silakan hubungi @mr7wanjroke jika ada kendala.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global callback query handler."""
    query = update.callback_query
    await query.answer()
    
    logger.info("callback_query", user_id=update.effective_user.id, data=query.data)
    
    if query.data == "m_main_menu":
        await query.message.edit_text(
            "Kembali ke Menu Utama:",
            reply_markup=start_menu_keyboard()
        )
    # Add more logic based on callback data prefixes (s_, u_, p_, i_, m_, a_)
    else:
        await query.message.reply_text(f"Fitur untuk {query.data} sedang dalam pengembangan.")

def register_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    # Add more handlers as needed
