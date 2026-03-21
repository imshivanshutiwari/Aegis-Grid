"""Aegis-Grid Tactical API — PHASE 2

Enhanced with:
- Agent graph integration in the WebSocket lifecycle
- Audit log API endpoint
- Proper time import
- Reasoning buffer broadcast
"""
import asyncio
import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .simulator import ScenarioSimulator
from .core.audit_log import audit_logger

app = FastAPI(title="Aegis-Grid: Tactical AI Suite", version="2.0.1")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared simulator instance
simulator = ScenarioSimulator()


@app.on_event("startup")
async def startup_event():
    """Start the simulator background task on server boot."""
    asyncio.create_task(simulator.run())


@app.get("/api/audit-log")
async def get_audit_log():
    """REST endpoint to retrieve recent tactical decisions."""
    return {"decisions": audit_logger.get_recent_decisions(limit=50)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Primary WebSocket endpoint for real-time C2 data streaming."""
    await websocket.accept()
    print("WebSocket CONNECTED")
    try:
        while True:
            # Send current state (units, alerts, reasoning)
            state = simulator.get_state()

            # Format for frontend consumption
            # Send units
            await websocket.send_json({
                "channel": "units.positions",
                "data": state["units"]
            })

            # Send alerts
            if state.get("alerts"):
                await websocket.send_json({
                    "channel": "threats.alerts",
                    "data": state["alerts"]
                })

            # Send agent reasoning logs
            if state.get("reasoning"):
                for log_entry in state["reasoning"]:
                    await websocket.send_json({
                        "channel": "agents.reasoning",
                        "data": log_entry
                    })

            # Listen for commands with a short timeout
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                command_data = json.loads(data)
                cmd = command_data.get("command")
                if cmd:
                    simulator.handle_command(cmd)
                    # Send confirmation
                    await websocket.send_json({
                        "channel": "agents.reasoning",
                        "data": {
                            "role": "SYSTEM",
                            "content": f"🎯 COMMAND RECEIVED: {cmd}. Executing tactical protocol...",
                            "timestamp": time.time()
                        }
                    })
            except asyncio.TimeoutError:
                pass

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WebSocket DISCONNECTED")
    except Exception as e:
        print(f"WebSocket Error: {e}")
