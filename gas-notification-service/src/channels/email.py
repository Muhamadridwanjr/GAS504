from src.config import settings
from src.lib.logger import logger
from src.core.exceptions import ChannelError
import smtplib
from email.message import EmailMessage

async def send_email_message(notification_data: dict):
    # Implementation using standard async mailers or sync smtplib if inside a Celery thread.
    # We will use sync inside Celery task wrappers
    
    if not settings.smtp_host or not settings.smtp_user:
        logger.warning("SMTP Config missing. Skipping email notification.")
        return
        
    user_email = "dummy@example.com" # In reality, fetch from gas-user-service similar to telegram
    
    msg = EmailMessage()
    msg.set_content(notification_data.get("message", ""))
    msg['Subject'] = notification_data.get("title", "GAS Strategy Notification")
    msg['From'] = settings.smtp_from
    msg['To'] = user_email
    
    try:
        # Since this runs in a Celery worker pool, we run blocking smtplib normally
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        server.starttls()
        # server.login(settings.smtp_user, settings.smtp_password) # Commented out for dummy dev config
        # server.send_message(msg)
        server.quit()
        logger.info(f"Simulated sending email to {user_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {e}")
        raise ChannelError(f"SMTP error: {e}")
