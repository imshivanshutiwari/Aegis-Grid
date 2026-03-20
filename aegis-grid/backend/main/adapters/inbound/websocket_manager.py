import asyncio
from typing import Dict, Any, List
from fastapi import WebSocket, WebSocketDisconnect
import logging
import json
try:
    import msgpack
except ImportError:
    msgpack = None

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections, pub/sub channels, msgpack binary frames, and backpressure."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.message_buffer: Dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.message_buffer[websocket] = 0
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            del self.message_buffer[websocket]
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_binary(self, message: Dict[str, Any], channel: str = "broadcast"):
        """Broadcast using msgpack for compression if available."""
        if msgpack:
            payload = msgpack.packb({"channel": channel, "data": message})
            for connection in list(self.active_connections):
                if self.message_buffer[connection] > 1000 and channel != "threats.alerts":
                    # Backpressure: drop non-alert updates
                    continue
                try:
                    await connection.send_bytes(payload)
                except WebSocketDisconnect:
                    self.disconnect(connection)
                except Exception as e:
                    logger.error(f"Error sending msgpack: {e}")
                    self.disconnect(connection)
        else:
            await self.broadcast_json({"channel": channel, "data": message})

    async def broadcast_json(self, message: Dict[str, Any]):
        """Fallback to JSON if msgpack missing."""
        payload = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except WebSocketDisconnect:
                self.disconnect(connection)
            except Exception as e:
                self.disconnect(connection)

manager = ConnectionManager()
