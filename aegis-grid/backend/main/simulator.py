import asyncio
import random
import uuid
import logging
from typing import List, Dict, Any
from main.adapters.inbound.websocket_manager import manager

logger = logging.getLogger(__name__)

class ScenarioSimulator:
    """Simulates live tactical data (drones, hostiles) moving over time."""
    def __init__(self):
        self.units: List[Dict[str, Any]] = []
        self._initialize_scenario()

    def _initialize_scenario(self):
        # Base coordinates near Taiwan Strait (approx 120.5 E, 24.5 N)
        for _ in range(50):
            self.units.append({
                "id": str(uuid.uuid4()),
                "unit_type": "FRIENDLY",
                "lon": 120.5 + random.uniform(-0.5, 0.5),
                "lat": 24.5 + random.uniform(-0.5, 0.5),
                "velocity_lon": random.uniform(-0.001, 0.001),
                "velocity_lat": random.uniform(-0.001, 0.001),
            })

        for _ in range(10):
            self.units.append({
                "id": str(uuid.uuid4()),
                "unit_type": "HOSTILE",
                "lon": 120.5 + random.uniform(-1.0, 1.0),
                "lat": 24.5 + random.uniform(-1.0, 1.0),
                "velocity_lon": random.uniform(-0.002, 0.002),
                "velocity_lat": random.uniform(-0.002, 0.002),
                "threat_level": "HIGH",
                "threat_score": random.uniform(0.6, 0.9)
            })

    async def run(self):
        """Background loop to update positions and broadcast."""
        logger.info("Starting live scenario simulator at 1Hz...")
        target_lon, target_lat = 120.5, 24.5
        
        while True:
            await asyncio.sleep(1.0)
            for unit in self.units:
                if unit["unit_type"] == "HOSTILE":
                    # Move towards center slightly
                    dx = target_lon - unit["lon"]
                    dy = target_lat - unit["lat"]
                    dist = (dx**2 + dy**2)**0.5
                    if dist > 0.1:
                        unit["velocity_lon"] = (dx/dist) * 0.005
                        unit["velocity_lat"] = (dy/dist) * 0.005
                
                unit["lon"] += unit["velocity_lon"]
                unit["lat"] += unit["velocity_lat"]

                # Keep them in bounds vaguely
                if abs(unit["lon"] - target_lon) > 5.0: unit["velocity_lon"] *= -1
                if abs(unit["lat"] - target_lat) > 5.0: unit["velocity_lat"] *= -1

            await manager.broadcast_json({"channel": "units.positions", "data": self.units})

            # Replenish hostiles if all were neutralized
            if len([u for u in self.units if u["unit_type"] == "HOSTILE"]) < 3 and random.random() < 0.05:
                self.units.append({
                    "id": str(uuid.uuid4()),
                    "unit_type": "HOSTILE",
                    "lon": target_lon + random.uniform(-2.0, 2.0),
                    "lat": target_lat + random.uniform(-2.0, 2.0),
                    "velocity_lon": random.uniform(-0.002, 0.002),
                    "velocity_lat": random.uniform(-0.002, 0.002),
                    "threat_level": "HIGH",
                    "threat_score": random.uniform(0.6, 0.9)
                })

            # Occasionally send an alert
            if random.random() < 0.1:
                hostiles = [u for u in self.units if u["unit_type"] == "HOSTILE"]
                if hostiles:
                    h = random.choice(hostiles)
                    alert = {
                        "id": str(uuid.uuid4()),
                        "unit_id": h["id"],
                        "threat_level": "CRITICAL",
                        "threat_score": 0.95,
                        "description": f"INCURSION: Hostile unit {h['id'][:4]} identified in corridor.",
                        "lon": h["lon"],
                        "lat": h["lat"]
                    }
                    # Send single alert object, not a list
                    await manager.broadcast_json({"channel": "threats.alerts", "data": alert})

                    # Also send mock agent reasoning
                    await manager.broadcast_json({
                        "channel": "agents.reasoning",
                        "data": {"role": "supervisor", "content": "CRITICAL THREAT DETECTED. Awakening Intel Analyst."}
                    })

    def handle_command(self, command: str):
        """Reacts to commander input."""
        if command == "EXECUTE":
            # "Neutralize" all current hostiles
            self.units = [u for u in self.units if u["unit_type"] != "HOSTILE"]
            # Add some new ones later or just keep it clear for a bit
            logger.info("EXECUTE: All hostiles neutralized.")
        elif command == "ABORT":
            # Maybe just log for now or reset velocities
            logger.info("ABORT: Engagement halted.")

simulator = ScenarioSimulator()
