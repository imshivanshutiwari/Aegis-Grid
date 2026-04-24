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


async def _agent_analysis_runner(context: dict) -> list:
    """
    Agent analysis callback injected into the simulator.
    Encapsulates all knowledge of the agents layer so the simulator
    does not need to import it directly.
    """
    from .agents.graph import (
        build_agent_graph, supervisor_node, intel_node, planner_node, commander_hitl_node
    )
    from .agents.models import AgentState, AgentRole

    initial_state: AgentState = {
        "agent_id": f"AEGIS-{int(time.time())}",
        "role": AgentRole.SUPERVISOR,
        "messages": [],
        "bdi": {
            "beliefs": {
                "units": context["units"],
                "is_jamming": context["is_jamming"],
                "timestamp": context["timestamp"],
            },
            "desires": [],
            "intentions": [],
        },
        "memory": {
            "sensory_buffer": [],
            "working_memory": {},
            "episodic_memory": [],
            "semantic_memory": {},
        },
        "current_plan": None,
        "confidence": 0.5,
        "reflection_count": 0,
        "status": "INITIALIZING",
    }

    graph = build_agent_graph()
    result = initial_state
    node_funcs = [
        ("supervisor", supervisor_node),
        ("intel_analyst", intel_node),
        ("tactical_planner", planner_node),
        ("commander_hitl", commander_hitl_node),
    ]
    for _name, node_fn in node_funcs:
        update = await node_fn(result)
        for key, value in update.items():
            result[key] = value

    # Extract reasoning entries from the last 4 messages (one per node)
    reasoning_entries = []
    for msg in result.get("messages", [])[-4:]:
        reasoning_entries.append({
            "role": msg.sender_id if hasattr(msg, "sender_id") else "SYSTEM",
            "content": msg.content if hasattr(msg, "content") else str(msg),
            "timestamp": time.time(),
        })
    return reasoning_entries


# Shared simulator instance — agent runner injected to avoid architecture violation
simulator = ScenarioSimulator(agent_runner=_agent_analysis_runner)


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
