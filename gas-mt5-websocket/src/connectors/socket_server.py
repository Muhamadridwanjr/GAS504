import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from pydantic import ValidationError

from src.config import settings
from src.lib.logger import log
from src.models.messages import (
    RegisterMessage, TickMessage, OhlcMessage, 
    PingMessage, PongMessage, ErrorMessage
)
from src.processor.forwarder import forwarder

class SocketServerConnector:
    def __init__(self):
        self.port = settings.SOCKET_PORT
        self.host = "0.0.0.0"
        self._server = None
        self._running = False
        self.clients = set()

    async def start(self):
        log.info(f"Starting Socket Server Connector on ws://{self.host}:{self.port}")
        self._running = True
        
        async with websockets.serve(self._handle_client, self.host, self.port) as server:
            self._server = server
            await asyncio.Future()  # Run forever

    async def _handle_client(self, websocket, path):
        log.info(f"New client connected from {websocket.remote_address}")
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                await self._process_message(websocket, message)
        except (ConnectionClosedOK, ConnectionClosedError):
            log.info(f"Client {websocket.remote_address} disconnected")
        except Exception as e:
            log.error(f"Error handling client {websocket.remote_address}: {e}")
        finally:
            self.clients.remove(websocket)

    async def _process_message(self, websocket, message_str: str):
        try:
            data = json.loads(message_str)
            msg_type = data.get("type")

            if msg_type == "register":
                msg = RegisterMessage(**data)
                log.info(f"EA registered symbols: {msg.symbols}")
                # In a more complex setup, we might track which symbols each client provides
                
            elif msg_type == "tick":
                msg = TickMessage(**data)
                await forwarder.forward_tick(msg)
                
            elif msg_type == "ohlc":
                msg = OhlcMessage(**data)
                await forwarder.forward_ohlc(msg)
                
            elif msg_type == "ping":
                await websocket.send(PongMessage().model_dump_json())
                
            else:
                log.warning(f"Unknown message type: {msg_type}")
                await websocket.send(ErrorMessage(message=f"Unknown message type: {msg_type}").model_dump_json())

        except json.JSONDecodeError:
            log.error(f"Invalid JSON received: {message_str}")
            await websocket.send(ErrorMessage(message="Invalid JSON").model_dump_json())
        except ValidationError as e:
            log.error(f"Message validation error: {e}")
            await websocket.send(ErrorMessage(message=f"Validation error: {e.errors()}").model_dump_json())
        except Exception as e:
            log.error(f"Unexpected error processing message: {e}")
            await websocket.send(ErrorMessage(message=f"Server error: {str(e)}").model_dump_json())

    def stop(self):
        log.info("Stopping Socket Server Connector")
        self._running = False
        if self._server:
            self._server.close()
