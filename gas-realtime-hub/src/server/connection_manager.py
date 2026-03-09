from fastapi import WebSocket
from typing import Dict, List, Set
from src.lib.logger import logger
import json

class ConnectionManager:
    def __init__(self):
        # connection_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # channel_name -> set of connection_ids
        self.subscriptions: Dict[str, Set[str]] = {}

    def connect(self, connection_id: str, websocket: WebSocket):
        self.active_connections[connection_id] = websocket
        logger.info(f"Client connected: {connection_id}. Total: {len(self.active_connections)}")

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from subscriptions
        empty_channels = []
        for channel, conns in self.subscriptions.items():
            if connection_id in conns:
                conns.remove(connection_id)
            if not conns:
                empty_channels.append(channel)
                
        for channel in empty_channels:
            del self.subscriptions[channel]
            
        logger.info(f"Client disconnected: {connection_id}. Total: {len(self.active_connections)}")

    def subscribe(self, connection_id: str, channels: List[str]):
        if connection_id not in self.active_connections:
            return
            
        for channel in channels:
            if channel not in self.subscriptions:
                self.subscriptions[channel] = set()
            self.subscriptions[channel].add(connection_id)
            
        logger.debug(f"Client {connection_id} subscribed to {channels}")

    def unsubscribe(self, connection_id: str, channels: List[str]):
        if connection_id not in self.active_connections:
            return
            
        empty_channels = []
        for channel in channels:
            if channel in self.subscriptions and connection_id in self.subscriptions[channel]:
                self.subscriptions[channel].remove(connection_id)
                if not self.subscriptions[channel]:
                    empty_channels.append(channel)
                    
        for channel in empty_channels:
            del self.subscriptions[channel]
            
        logger.debug(f"Client {connection_id} unsubscribed from {channels}")

    async def broadcast_to_channel(self, channel: str, message: dict):
        if channel not in self.subscriptions:
            return
            
        dead_connections = []
        message_str = json.dumps(message)
        
        for connection_id in self.subscriptions[channel]:
            ws = self.active_connections.get(connection_id)
            if ws:
                try:
                    await ws.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error sending message to {connection_id}: {e}")
                    dead_connections.append(connection_id)
                    
        for connection_id in dead_connections:
            self.disconnect(connection_id)

    def get_active_count(self) -> int:
        return len(self.active_connections)

manager = ConnectionManager()
