from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
from typing import Dict
import logging
from api.stream_manager import StreamManager
from agents.orchestrator import run_orchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="KAVACH-SIGMA API", version="1.0.0")
manager = StreamManager()

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint to verify API status.

    Returns:
        Dict[str, str]: A status message.
    """
    return {"status": "online", "message": "KAVACH-SIGMA API is running"}

@app.websocket("/ws/spectrum")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time spectrum data streaming and analysis.

    Args:
        websocket (WebSocket): The incoming WebSocket connection.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive raw I/Q signal data or trigger a simulation
            data = await websocket.receive_text()
            logger.info(f"Received request: {data}")

            # Here we would normally receive actual RF data, but for simulation
            # we trigger the orchestrator which generates a mock signal
            response = run_orchestrator(data)

            await manager.broadcast(str(response))
            await asyncio.sleep(0.1) # Simulate processing delay

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")

@app.post("/api/v1/trigger")
async def trigger_analysis(data: dict) -> dict:
    """
    HTTP POST endpoint to trigger a one-off signal analysis.

    Args:
        data (dict): The input request data containing signal parameters.

    Returns:
        dict: The result of the orchestrator pipeline.
    """
    import json
    result = run_orchestrator(json.dumps(data))
    return {"result": result}
