import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from main.api.websocket import router, manager
import asyncio

app = FastAPI()
app.include_router(router)

def test_websocket_pub_sub():
    client = TestClient(app)
    with client.websocket_connect("/ws/units.position", subprotocols=["permessage-deflate"]) as websocket:
        assert len(manager.active_connections["units.position"]) >= 1
