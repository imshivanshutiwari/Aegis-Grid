import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .simulator import ScenarioSimulator

app = FastAPI(title="Aegis-Grid Tactical API")

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
    # Start the simulator background task
    asyncio.create_task(simulator.run())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket CONNECTED")
    try:
        while True:
            # Send current state
            state = simulator.get_state()
            await websocket.send_json(state)
            
            # Listen for commands with a short timeout
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                command_data = json.loads(data)
                cmd = command_data.get("command")
                if cmd:
                    simulator.handle_command(cmd)
                    # Broadcast confirmation to logs
                    await websocket.send_json({
                        "id": f"LOG-{int(time.time())}",
                        "type": "log",
                        "message": f"COMMAND RECEIVED: {cmd}. Executing tactical protocol...",
                        "timestamp": time.time()
                    })
            except asyncio.TimeoutError:
                pass
            
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WebSocket DISCONNECTED")
    except Exception as e:
        print(f"WebSocket Error: {e}")
