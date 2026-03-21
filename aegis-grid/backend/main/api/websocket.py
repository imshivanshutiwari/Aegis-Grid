from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set, Any
import asyncio
import json
import ormsgpack
from datetime import datetime

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Using a Dict of Set for topic-based pub/sub
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "units.position": set(),
            "threats.alerts": set(),
            "agents.reasoning": set(),
            "commander.approvals": set()
        }
        self.buffers: Dict[str, list] = {
            "units.position": []
        }
        self.MAX_BUFFER = 1000

    async def connect(self, websocket: WebSocket, topic: str):
        # We assume standard setup accepts the websocket
        await websocket.accept(subprotocol="permessage-deflate")
        if topic not in self.active_connections:
            self.active_connections[topic] = set()
        self.active_connections[topic].add(websocket)
        # Start heartbeat monitor for this connection
        asyncio.create_task(self._heartbeat(websocket, topic))

    def disconnect(self, websocket: WebSocket, topic: str):
        if topic in self.active_connections and websocket in self.active_connections[topic]:
            self.active_connections[topic].remove(websocket)

    async def broadcast_json(self, topic: str, message: dict):
        # Backpressure control
        if topic == "units.position":
            self.buffers[topic].append(message)
            if len(self.buffers[topic]) > self.MAX_BUFFER:
                # Drop non-critical
                self.buffers[topic] = self.buffers[topic][-self.MAX_BUFFER//2:]

        # Async broadcast
        if topic in self.active_connections:
            for connection in self.active_connections[topic]:
                try:
                    await connection.send_json(message)
                except Exception:
                    self.disconnect(connection, topic)

    async def broadcast_binary(self, topic: str, message: dict):
        if topic in self.active_connections:
            # msgpack binary frames
            binary_data = ormsgpack.packb(message)
            for connection in self.active_connections[topic]:
                try:
                    await connection.send_bytes(binary_data)
                except Exception:
                    self.disconnect(connection, topic)

    async def _heartbeat(self, websocket: WebSocket, topic: str):
        try:
            while True:
                await asyncio.sleep(30) # ping 30s
                await websocket.send_text("ping")
                # Wait for pong 10s
                try:
                    response = await asyncio.wait_for(websocket.receive_text(), timeout=10)
                    if response != "pong":
                        raise WebSocketDisconnect()
                except asyncio.TimeoutError:
                    raise WebSocketDisconnect()
        except WebSocketDisconnect:
            self.disconnect(websocket, topic)
        except Exception:
            self.disconnect(websocket, topic)

manager = ConnectionManager()

@router.websocket("/ws/{topic}")
async def websocket_endpoint(websocket: WebSocket, topic: str):
    await manager.connect(websocket, topic)
    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, topic)
