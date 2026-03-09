import httpx
import structlog
from typing import Optional, Dict, Any

logger = structlog.get_logger(__name__)

async def fetch_service_data(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper to fetch data from internal GAS services."""
    async with httpx.AsyncClient() as client:
        try:
            logger.info("calling_internal_service", url=url)
            resp = await client.get(url, params=params, timeout=10.0)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.warning("service_response_error", url=url, status=resp.status_code)
                return {}
        except Exception as e:
            logger.error("service_connection_error", url=url, error=str(e))
            return {}
