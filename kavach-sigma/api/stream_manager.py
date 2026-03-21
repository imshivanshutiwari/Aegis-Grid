from fastapi import WebSocket
from typing import List
import logging

logger = logging.getLogger(__name__)

class StreamManager:
    """
    Manages active WebSocket connections for live spectrum streaming.
    """

    def __init__(self):
        """
        Initializes the StreamManager with an empty list of active connections.
        """
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accepts a new WebSocket connection and adds it to the active list.

        Args:
            websocket (WebSocket): The new WebSocket client.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New client connected.")

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Removes a WebSocket connection from the active list.

        Args:
            websocket (WebSocket): The WebSocket client to remove.
        """
        self.active_connections.remove(websocket)
        logger.info("Client removed from active connections.")

    async def broadcast(self, message: str) -> None:
        """
        Broadcasts a message to all connected clients.

        Args:
            message (str): The string message to send.
        """
        for connection in self.active_connections:
            await connection.send_text(message)
        logger.debug(f"Broadcasted message to {len(self.active_connections)} clients.")
