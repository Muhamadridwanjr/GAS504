"""
Proxy handler for GAS Gateway API.
Forwards all requests to upstream services.
Injects:
  - X-Internal-Key: for backend service authentication
  - X-User-ID: extracted from JWT payload (if authenticated user)
  - X-Request-ID: trace ID for observability
"""
import uuid
import httpx
import asyncio
from fastapi import Request, Response
from src.config import settings
from src.utils.logger import logger


async def forward_request(request: Request, target_url: str) -> Response:
    """
    Forwards the incoming request to the target internal service.
    Injects security headers transparently.
    """
    async with httpx.AsyncClient() as client:
        method = request.method
        headers = dict(request.headers)

        # Remove host to avoid conflicts with target service
        headers.pop("host", None)
        headers.pop("content-length", None)  # httpx recalculates this

        # ── Security injection ──────────────────────────────────────────
        # Inject X-Internal-Key so backend services accept this request
        headers["X-Internal-Key"] = settings.GATEWAY_API_KEY

        # Inject authenticated user ID (forwarded from JWT decoded in AuthMiddleware)
        user = getattr(request.state, "user", None)
        if user:
            user_id = user.get("sub") or user.get("user_id") or user.get("id", "")
            if user_id:
                headers["X-User-ID"] = str(user_id)
            # Forward user role for RBAC at service level
            role = user.get("role") or user.get("user_role", "user")
            headers["X-User-Role"] = str(role)

        # ── Observability ───────────────────────────────────────────────
        # Propagate or generate request trace ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        headers["X-Request-ID"] = request_id

        body = await request.body()
        params = request.query_params

        try:
            logger.debug(
                "Forwarding request",
                method=method,
                url=target_url,
                request_id=request_id,
            )

            response = await client.request(
                method,
                target_url,
                headers=headers,
                params=params,
                content=body,
                follow_redirects=True,
                timeout=60.0,
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        except httpx.RequestError as e:
            logger.warning(
                "Backend service unavailable",
                error=str(e),
                url=target_url,
                request_id=request_id,
            )
            return Response(
                content='{"status":"service_unavailable","detail":"Backend service is not ready."}',
                status_code=503,
                media_type="application/json",
            )
        except Exception as e:
            logger.error("Unexpected proxy error", error=str(e), url=target_url)
            return Response(
                content='{"status":"gateway_error","detail":"Internal gateway error."}',
                status_code=500,
                media_type="application/json",
            )

async def forward_websocket(client_ws, target_url: str):
    """
    Proxies a WebSocket connection from client to an internal service.
    Handles disconnect gracefully and cleans up both sides.
    """
    import websockets
    try:
        async with websockets.connect(target_url, ping_interval=20, ping_timeout=10) as backend_ws:
            logger.debug("WebSocket proxy established", url=target_url)

            async def client_to_backend():
                try:
                    while True:
                        msg = await client_ws.receive_text()
                        await backend_ws.send(msg)
                except Exception:
                    pass

            async def backend_to_client():
                try:
                    while True:
                        msg = await backend_ws.recv()
                        await client_ws.send_text(msg)
                except Exception:
                    pass

            done, pending = await asyncio.wait(
                [
                    asyncio.create_task(client_to_backend()),
                    asyncio.create_task(backend_to_client()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
    except Exception as e:
        logger.warning("WebSocket proxy error", error=str(e), url=target_url)
        try:
            await client_ws.close(code=1011)
        except Exception:
            pass
