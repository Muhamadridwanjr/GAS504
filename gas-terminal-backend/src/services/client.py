"""
GAS Terminal Backend – HTTP client for calling upstream GAS services.
Uses httpx with connection pooling and error handling.
"""
import httpx
import structlog
from typing import Optional, Any

logger = structlog.get_logger(__name__)

# Shared async client (created once, reused)
_client: Optional[httpx.AsyncClient] = None


async def get_client() -> httpx.AsyncClient:
    """Get or create the shared httpx async client."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )
    return _client


async def close_client():
    """Close the shared client (called on shutdown)."""
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


async def fetch_json(
    url: str,
    method: str = "GET",
    params: Optional[dict] = None,
    json_body: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: float = 15.0,
) -> dict[str, Any]:
    """
    Fetch JSON from an upstream service.
    Returns the parsed JSON on success, or a fallback error dict.
    """
    client = await get_client()
    try:
        logger.debug("upstream_request", url=url, method=method)
        resp = await client.request(
            method=method,
            url=url,
            params=params,
            json=json_body,
            headers=headers or {},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.TimeoutException:
        logger.warning("upstream_timeout", url=url)
        return {"error": "timeout", "detail": f"Timeout calling {url}"}
    except httpx.HTTPStatusError as e:
        logger.warning("upstream_http_error", url=url, status=e.response.status_code)
        return {"error": "http_error", "status": e.response.status_code}
    except Exception as e:
        logger.error("upstream_error", url=url, error=str(e))
        return {"error": "connection_error", "detail": str(e)}
