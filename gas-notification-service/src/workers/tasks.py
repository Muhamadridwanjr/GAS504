import asyncio
from celery.utils.log import get_task_logger
from src.workers.celery_app import celery_app
from src.channels.telegram import send_telegram_message
from src.channels.web import send_web_push
from src.channels.email import send_email_message

logger = get_task_logger(__name__)

async def process_channels_async(notification_data: dict):
    channels = notification_data.get("channels", [])
    tasks = []
    
    if "telegram" in channels:
        tasks.append(send_telegram_message(notification_data))
    if "web" in channels:
        tasks.append(send_web_push(notification_data))
    if "email" in channels:
        tasks.append(send_email_message(notification_data))
        
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Channel delivery failed: {r}")

def run_async(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_task(self, notification_data: dict):
    logger.info(f"Processing notification task for user: {notification_data.get('user_id')}")
    
    try:
        # We spawn an async loop because our channel dispatchers use async functions
        # (e.g. httpx, python-telegram-bot)
        run_async(process_channels_async(notification_data))
        logger.info("Notification successfully processed.")
    except Exception as exc:
        logger.error(f"Task failed, retrying: {exc}")
        raise self.retry(exc=exc)
