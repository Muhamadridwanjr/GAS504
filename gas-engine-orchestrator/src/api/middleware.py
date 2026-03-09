import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
from typing import Callable, Awaitable
from src.lib.config import settings
from src.lib.logger import log

class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            return await call_next(request)
        except Exception as e:
            log.error(f"Uncaught exception: {e}")
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        # Allow healthcheck and docs without token
        if request.url.path in ["/health", "/docs", "/openapi.json", "/signal/orchestrated"]:
            return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing Authorization header"})
            
        token = auth_header.split(" ")[1]
        try:
            # Di sini kita memverifikasi JWT dari Gateway
            # Jika ekosistem Gateway memakai public key atau semacamnya,
            # pastikan JWT_SECRET_KEY sama di orchestrator.
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            request.state.user = payload
        except jwt.ExpiredSignatureError:
            log.warning("Token expired")
            return JSONResponse(status_code=401, content={"detail": "Token Expired"})
        except jwt.PyJWTError as e:
            log.warning(f"Invalid token: {e}")
            return JSONResponse(status_code=401, content={"detail": "Invalid Token"})
            
        return await call_next(request)

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        log.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
        return response
