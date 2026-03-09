from telegram import Bot
from telegram.constants import ParseMode
from src.config import settings
from src.lib.logger import logger
from src.core.exceptions import ChannelError
import httpx

async def get_user_chat_id(user_id: str) -> str:
    # Fetch chat_id from gas-user-service
    url = f"{settings.user_service_url}/internal/users/{user_id}/preferences"
    headers = {"X-API-Key": settings.internal_api_key}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("telegram_chat_id")
    except Exception as e:
        logger.error(f"Failed to fetch user preferences for {user_id}: {e}")
    return None

async def send_telegram_message(notification_data: dict):
    if not settings.telegram_bot_token:
        logger.warning("Telegram Bot Token is not set. Skipping telegram notification.")
        return

    user_id = notification_data.get("user_id")
    chat_id = await get_user_chat_id(user_id)
    
    if not chat_id:
        logger.warning(f"No Telegram chat_id found for user {user_id}")
        return

    bot = Bot(token=settings.telegram_bot_token)
    
    title = notification_data.get("title", "")
    message = notification_data.get("message", "")
    
    # Basic formatting
    text = f"🚨 *{title}*\n\n{message}"
    
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"Sent telegram message to chat_id {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send telegram message to {chat_id}: {e}")
        raise ChannelError(f"Telegram API error: {e}")
