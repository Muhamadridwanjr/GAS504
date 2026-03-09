from typing import Dict, Any
import httpx
from src.config import settings
from src.lib.logger import logger


class NotificationClient:
    """HTTP client for communicating with gas-notification-service."""

    BASE_URL: str = settings.NOTIFICATION_SERVICE_URL
    API_KEY: str = settings.NOTIFICATION_SERVICE_API_KEY

    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        data: Dict[str, Any],
    ) -> bool:
        """
        Send a notification to a user via gas-notification-service.
        Returns True on success, False on failure (non-critical).
        """
        headers = {"X-API-Key": self.API_KEY}
        payload = {
            "user_id": user_id,
            "type": notification_type,
            "data": data,
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/internal/notify",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                return True
        except httpx.HTTPStatusError as e:
            logger.warning(
                f"Notification service HTTP error {e.response.status_code}: {e.response.text}"
            )
            return False
        except httpx.RequestError as e:
            logger.warning(f"Notification service unavailable: {e}")
            return False


notification_client = NotificationClient()
