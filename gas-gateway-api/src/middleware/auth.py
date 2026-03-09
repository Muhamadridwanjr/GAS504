from fastapi import Request
from starlette.responses import JSONResponse
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from src.config import settings
from src.utils.logger import logger

PUBLIC_PATHS = [
    "/health",
    "/api/health",
    "/api/v1/health",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/health",
    "/api/auth/v1/login",
    "/api/auth/v1/register",
    "/api/auth/v1/health",
    "/api/v1/telegram/webhook",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/",
    "/favicon.ico"
]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        logger.debug("AuthMiddleware checking path", path=path)
        
        # Check if path is public
        is_public = any(path == p or (p != "/" and path.startswith(p)) for p in PUBLIC_PATHS)
        if is_public or path == "/" or getattr(request.state, "api_authenticated", False):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Missing or invalid token", path=path)
            if settings.DEBUG:
                logger.warning("DEBUG MODE: Bypassing authentication", path=path)
                return await call_next(request)
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid token"}
            )

        token = auth_header.split(" ")[1]
        try:
            # Note: Supabase uses HS256 by default for internal projects
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=["HS256"],
                options={"verify_aud": False} # Supabase might have specific aud
            )
            request.state.user = payload
        except JWTError as e:
            logger.warning("Token verification failed", error=str(e), path=path)
            if settings.DEBUG:
                logger.warning("DEBUG MODE: Bypassing failed authentication", path=path)
                return await call_next(request)
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )

        return await call_next(request)
