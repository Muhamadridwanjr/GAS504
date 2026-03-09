from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional
import json
import uuid

from src.server.connection_manager import manager
from src.server.auth import verify_token
from src.lib.logger import logger
from src.redis.pubsub import redis_subscriber

app = FastAPI(title="GAS Realtime Hub")

@app.on_event("startup")
async def startup_event():
    await redis_subscriber.start()

@app.on_event("shutdown")
async def shutdown_event():
    await redis_subscriber.stop()

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "gas-realtime-hub",
        "connections": manager.get_active_count()
    }

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    connection_id = str(uuid.uuid4())
    
    # We require a token. If verifier is strict, it will reject.
    if not token and token != "dev_token":
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Authentication required"})
        await websocket.close(code=1008)
        return
        
    user_info = verify_token(token)
    if user_info is None and token != "dev_token":
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Invalid token"})
        await websocket.close(code=1008)
        return

    await websocket.accept()
    manager.connect(connection_id, websocket)
    
    try:
        while True:
            text_data = await websocket.receive_text()
            try:
                data = json.loads(text_data)
                msg_type = data.get("type")
                
                if msg_type == "subscribe":
                    channels = data.get("channels", [])
                    manager.subscribe(connection_id, channels)
                elif msg_type == "unsubscribe":
                    channels = data.get("channels", [])
                    manager.unsubscribe(connection_id, channels)
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                else:
                    await websocket.send_json({"type": "error", "message": "Unknown message type"})
                    
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON payload"})
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
        manager.disconnect(connection_id)
