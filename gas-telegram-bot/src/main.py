import asyncio
from telegram.ext import ApplicationBuilder
from src.config import settings
from src.utils.logger import logger, setup_logger
from src.bot.handlers import register_handlers, BOT_COMMANDS
from src.services import bot_api_client
from src.workers.runner import run_workers


async def _keepalive():
    """Keep the event loop alive while polling runs."""
    while True:
        await asyncio.sleep(3600)


async def main():
    setup_logger()
    logger.info("starting_gas_telegram_bot")

    if not settings.TELEGRAM_BOT_TOKEN or "dummy" in settings.TELEGRAM_BOT_TOKEN:
        logger.error("missing_bot_token", message="Set a valid TELEGRAM_BOT_TOKEN in .env")
        return

    try:
        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
        register_handlers(application)
        logger.info("running_in_polling_mode")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        # Register bot commands after bot is fully running
        try:
            await application.bot.set_my_commands(BOT_COMMANDS)
            logger.info("bot_commands_registered", count=len(BOT_COMMANDS))
            print(f"[BOT COMMANDS] Registered {len(BOT_COMMANDS)} commands")
        except Exception as e:
            logger.warning("bot_commands_failed", error=str(e))
            print(f"[BOT COMMANDS] Failed: {e}")

        # Run bot polling + worker pool concurrently on the same event loop
        await asyncio.gather(
            _keepalive(),
            run_workers(application.bot),
            return_exceptions=True,
        )
    except Exception as e:
        logger.error("bot_runtime_error", error=str(e))
    finally:
        try:
            await bot_api_client.close()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal error: {e}")
