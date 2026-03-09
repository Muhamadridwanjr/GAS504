"""
GAS Gateway – EA Endpoints Proxy
Proxies /api/gas/{path} → terminal-backend /terminal/gas/{path}
These are the endpoints consumed by GASSTRATEGYEAPRO v4.0 EA.
"""
from fastapi import APIRouter, Request
from src.core.proxy_handler import forward_request
from src.config import settings

router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_gas_endpoints(request: Request, path: str):
    """
    Proxy all /api/gas/{path} requests to the terminal backend.
    EA endpoints:
      POST /api/gas/context          - EA sends full account+market context
      POST /api/gas/signal/request   - EA requests AI signal
      GET  /api/gas/signal/latest    - EA polls latest AI signal
      POST /api/gas/journal          - EA sends trade journal after close
      POST /api/gas/alert/pause      - EA sends pause alert
      POST /api/gas/signal/confirm   - EA confirms signal execution
    """
    target_url = f"{settings.TERMINAL_BACKEND_URL}/terminal/gas/{path}"
    return await forward_request(request, target_url)
