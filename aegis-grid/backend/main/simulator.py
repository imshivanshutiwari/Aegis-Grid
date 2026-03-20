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
        # Base coordinates near (0, 0)
        for _ in range(50):
            self.units.append({
                "id": str(uuid.uuid4()),
                "unit_type": "FRIENDLY",
                "lon": random.uniform(-1.0, 1.0),
                "lat": random.uniform(-1.0, 1.0),
                "velocity_lon": random.uniform(-0.005, 0.005),
                "velocity_lat": random.uniform(-0.005, 0.005),
            })

        for _ in range(10):
            self.units.append({
                "id": str(uuid.uuid4()),
                "unit_type": "HOSTILE",
                "lon": random.uniform(-2.0, 2.0),
                "lat": random.uniform(-2.0, 2.0),
                "velocity_lon": random.uniform(-0.01, 0.01),
                "velocity_lat": random.uniform(-0.01, 0.01),
                "threat_level": "HIGH",
                "threat_score": random.uniform(0.6, 0.9)
            })

    async def run(self):
        """Background loop to update positions and broadcast."""
        logger.info("Starting live scenario simulator at 1Hz...")
        while True:
            await asyncio.sleep(1.0)
            for unit in self.units:
                unit["lon"] += unit["velocity_lon"]
                unit["lat"] += unit["velocity_lat"]

                # Keep them in bounds vaguely
                if abs(unit["lon"]) > 3.0: unit["velocity_lon"] *= -1
                if abs(unit["lat"]) > 3.0: unit["velocity_lat"] *= -1

            await manager.broadcast_json({"channel": "units.positions", "data": self.units})

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
                        "description": f"Hostile unit breached exclusion zone at [{h['lon']:.2f}, {h['lat']:.2f}]",
                        "lon": h["lon"],
                        "lat": h["lat"]
                    }
                    await manager.broadcast_json({"channel": "threats.alerts", "data": [alert]})

                    # Also send mock agent reasoning
                    await manager.broadcast_json({
                        "channel": "agents.reasoning",
                        "data": {"role": "supervisor", "content": "CRITICAL THREAT DETECTED. Awakening Intel Analyst."}
                    })

simulator = ScenarioSimulator()
