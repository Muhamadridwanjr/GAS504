import asyncio
import json
import structlog
from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from src.config import settings

logger = structlog.get_logger(__name__)

class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("ws_connect", total=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("ws_disconnect", total=len(self.active_connections))

    async def broadcast(self, message: dict):
        dead = []
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for d in dead:
            self.disconnect(d)

manager = ConnectionManager()


async def _redis_price_feed(websocket: WebSocket, symbols: set):
    """Receive live tick updates from Redis Pub/Sub."""
    logger.info("starting_redis_feed", host=settings.REDIS_HOST, db=settings.REDIS_DB)
    try:
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True)
        pubsub = r.pubsub()
        await pubsub.subscribe("market:ticks")
        logger.info("redis_subscribed", channel="market:ticks", host=settings.REDIS_HOST, db=settings.REDIS_DB)
        
        async for message in pubsub.listen():
            logger.debug("redis_event", type=message.get("type"))
            if message["type"] == "message":
                msg_data = message["data"]
                # logger.debug("redis_data_raw", data=msg_data[:100])
                try:
                    data = json.loads(msg_data)
                    symbol = data.get("symbol", "").strip().upper()
                    
                    if not symbols or symbol in symbols or any(s in symbol for s in symbols):
                        ticks = data.get("ticks", [])
                        if ticks:
                            # Ambil tick terakhir saja
                            tick = ticks[-1]
                            # Try multiple possible price fields
                            price = tick.get("ask", tick.get("last", tick.get("bid", 0)))
                            
                            logger.info("tick_broadcast", symbol=symbol, price=price, clients_count=len(manager.active_connections))
                            
                            if not price: continue
                            
                            ts = tick.get("time_msc", tick.get("time", 0))
                            if ts > 9999999999: # if format is in ms
                                ts = ts / 1000.0
                                
                            await websocket.send_json({
                                "type": "price",
                                "symbol": symbol,
                                "price": float(price),
                                "timestamp": ts,
                            })
                        else:
                            # If no 'ticks' key, maybe it's a flat structure
                            price = data.get("price", data.get("ask", data.get("last", 0)))
                            if price:
                                await websocket.send_json({
                                    "type": "price",
                                    "symbol": symbol,
                                    "price": float(price),
                                    "timestamp": data.get("time", 0),
                                })
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error("parse_error", error=str(e), data=msg_data[:100])
    except (WebSocketDisconnect, ConnectionError, Exception) as e:
        logger.error(f"Redis feed connection error: {e}")
    finally:
        try:
            await pubsub.unsubscribe()
            await pubsub.close()
            await r.aclose()
        except:
            pass


async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket handler for terminal real-time feed."""
    await manager.connect(websocket)
    symbols = set()
    feed_task = asyncio.create_task(_redis_price_feed(websocket, symbols))
    msg_count = 0
    try:
        while True:
            data = await websocket.receive_text()
            msg_count += 1
            try:
                msg = json.loads(data)
                cmd = msg.get("command")
                logger.info("ws_command_received", cmd=cmd, symbol=msg.get("symbol"))
                if cmd == "ping":
                    await websocket.send_json({"type": "pong"})
                elif cmd == "subscribe":
                    sym = msg.get("symbol", "")
                    if sym:
                        symbols.add(sym)
                    await websocket.send_json({
                        "type": "subscribed",
                        "symbol": sym,
                    })
                elif cmd == "unsubscribe":
                    sym = msg.get("symbol", "")
                    if sym in symbols:
                        symbols.remove(sym)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        feed_task.cancel()
        try:
            await feed_task
        except asyncio.CancelledError:
            pass
        manager.disconnect(websocket)
