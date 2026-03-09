import httpx
from src.config import settings
from src.utils.logger import logger

class UserServiceClient:
    def __init__(self):
        self.base_url = settings.USER_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def create_profile(self, user_id: str, email: str, full_name: str = ""):
        """
        Calls gas-user-service to create a default profile for the user.
        """
        url = "/api/v1/profiles"
        payload = {
            "supabase_user_id": user_id,
            "email": email,
            "full_name": full_name
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            logger.info("user_profile_created", user_id=user_id, status="success")
            return response.json()
        except httpx.HTTPError as e:
            logger.error("user_profile_creation_failed", user_id=user_id, error=str(e))
            # Depending on business logic, we might want to retry or handle this gracefully
            return None

    async def close(self):
        await self.client.aclose()

user_service_client = UserServiceClient()
