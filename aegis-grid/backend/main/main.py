from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from main.infrastructure.config.settings import settings
from main.adapters.outbound.spatial_db_adapter import spatial_db
from main.adapters.outbound.vector_store_adapter import vector_store
from main.adapters.inbound.websocket_manager import manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    logger.info("Initializing Aegis-Grid backend services under IRON PROTOCOL...")
    await spatial_db.connect()
    await vector_store.initialize()
    yield
    logger.info("Shutting down Aegis-Grid backend services...")
    await spatial_db.close()

app = FastAPI(
    title="Aegis-Grid Core C2 API",
    version="1.0.0",
    lifespan=lifespan,
    description="Defense-grade Tactical Multi-Agent System"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Healthcheck endpoint."""
    return {"status": "healthy", "environment": settings.environment}

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time msgpack/JSON streaming."""
    await manager.connect(websocket)
    try:
        while True:
            # ReAct loop / Heartbeat incoming messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            else:
                logger.debug(f"Received WS command: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
