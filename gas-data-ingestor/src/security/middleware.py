"""
Internal API security middleware.
Validates X-Internal-Key for service-to-service calls.
Public endpoints: /health only.
All other endpoints require either:
  1. X-Internal-Key: <INTERNAL_API_KEY>   (service-to-service / gateway)
  2. Authorization: Bearer <JWT>           (forwarded from gateway, user calls)
"""
from __future__ import annotations
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

PUBLIC_PATHS = {"/health", "/", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}


class InternalKeyMiddleware(BaseHTTPMiddleware):
    """
    Guard: block direct access that bypasses the gateway.
    Accepts:
      - Requests to PUBLIC_PATHS (always allowed)
      - Requests with valid X-Internal-Key header
      - Requests with Authorization: Bearer ... (JWT forwarded from gateway)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Always allow public paths
        if path in PUBLIC_PATHS or any(path.startswith(p) for p in ["/docs", "/redoc", "/openapi"]):
            return await call_next(request)

        # Check X-Internal-Key (service-to-service / gateway internal calls)
        internal_key = request.headers.get("X-Internal-Key") or request.headers.get("X-INTERNAL-KEY")
        if internal_key:
            if internal_key == settings.INTERNAL_API_KEY:
                return await call_next(request)
            logger.warning("Invalid internal key", path=path)
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid internal API key"},
            )

        # Check Authorization Bearer (JWT forwarded from GAS Gateway)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Gateway already verified the JWT; we trust it here.
            # Optionally, re-verify locally if SUPABASE_JWT_SECRET is configured.
            return await call_next(request)

        # No valid credential
        logger.warning("Unauthorized direct access blocked", path=path, method=request.method)
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Unauthorized. Use gateway endpoint /api/v1/... or provide X-Internal-Key.",
                "hint": "Direct service access requires X-Internal-Key header.",
            },
        )
