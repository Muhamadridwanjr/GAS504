import asyncio
from telegram.ext import ApplicationBuilder
from src.config import settings
from src.utils.logger import logger, setup_logger
from src.bot.handlers import register_handlers
from src.services.gateway_client import gateway_client

async def main():
    # Setup logger
    setup_logger()
    logger.info("starting_gas_telegram_bot")

    # Initialize Gateway Client
    is_gateway_up = await gateway_client.check_health()
    if is_gateway_up:
        logger.info("gateway_connection_status", status="200 OK")
    else:
        logger.warning("gateway_connection_status", status="DOWN", url=settings.GATEWAY_URL)

    # Initialize Telegram Application
    if not settings.TELEGRAM_BOT_TOKEN or "your_bot_token" in settings.TELEGRAM_BOT_TOKEN:
        logger.error("missing_bot_token", message="Please set a valid TELEGRAM_BOT_TOKEN in .env")
        # Keep alive for healthcheck if needed, or exit
        return

    try:
        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
        register_handlers(application)

        if settings.TELEGRAM_WEBHOOK_URL:
            logger.info("running_in_webhook_mode", url=settings.TELEGRAM_WEBHOOK_URL)
            # await application.run_webhook(...)
        else:
            logger.info("running_in_polling_mode")
            try:
                await application.initialize()
                await application.start()
                await application.updater.start_polling()
            except Exception as e:
                logger.error("bot_polling_error", error=str(e), message="Bot failed to start polling. Check your token.")
            
            # Keep alive for healthcheck
            while True:
                await asyncio.sleep(3600)
                
    except Exception as e:
        logger.error("bot_runtime_error", error=str(e))
    finally:
        try:
            await gateway_client.close()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal error: {e}")
