from fastapi import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.config import settings
from src.utils.logger import logger

class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Paths that don't need API Key (Health, etc. - handled by PUBLIC_PATHS in auth)
        # But we check for API Key first for system-to-system
        
        api_key = request.headers.get("X-API-KEY")
        
        # If API Key is provided, validate it
        if api_key:
            if api_key == settings.GATEWAY_API_KEY:
                logger.debug("API Key authenticated", path=path)
                request.state.api_authenticated = True
                return await call_next(request)
            else:
                logger.warning("Invalid API Key provided", path=path)
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid API Key"}
                )
        
        # If no API key, proceed to next middleware (AuthMiddleware will handle JWT check)
        request.state.api_authenticated = False
        return await call_next(request)
