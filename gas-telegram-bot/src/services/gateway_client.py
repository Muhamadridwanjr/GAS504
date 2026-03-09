import httpx
from src.config import settings
from src.utils.logger import logger

class GatewayClient:
    def __init__(self):
        self.base_url = settings.GATEWAY_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def get_billing_status(self, user_id: int):
        try:
            response = await self.client.get(f"/api/v1/billing/status?user_id={user_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("failed_to_get_billing_status", user_id=user_id, error=str(e))
            return None

    async def check_health(self):
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()

gateway_client = GatewayClient()
