import httpx
from ..utils.logger import logger
from typing import Dict, Any, Optional

class HttpClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        await self.client.aclose()

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        try:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("HTTP GET Error", url=url, status_code=e.response.status_code, error=str(e))
            return {"error": f"Failed with status {e.response.status_code}"}
        except Exception as e:
            logger.error("HTTP GET Request Failed", url=url, error=str(e))
            return {"error": "Service unavailable"}

    async def post(self, url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        try:
            response = await self.client.post(url, json=json_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("HTTP POST Error", url=url, status_code=e.response.status_code, error=str(e))
            return {"error": f"Failed with status {e.response.status_code}"}
        except Exception as e:
            logger.error("HTTP POST Request Failed", url=url, error=str(e))
            return {"error": "Service unavailable"}

    # Placeholder for PUT, DELETE as needed

http_client = HttpClient()
