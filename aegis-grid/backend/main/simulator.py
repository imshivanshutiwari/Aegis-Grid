import asyncio
import random
import time
from typing import List, Dict

class ScenarioSimulator:
    def __init__(self):
        self.units = []
        self._initialize_scenario()
        self.is_jamming = False
        self.last_update = time.time()

    def _initialize_scenario(self):
        # Initializing units in the Indian Ocean region (near Port Blair, Andaman Sea)
        base_lat, base_lon = 11.6233, 92.7265
        
        # Friendly units
        for i in range(3):
            self.units.append({
                "id": f"F-{i+1}",
                "type": "friendly",
                "lat": base_lat + random.uniform(-0.05, 0.05),
                "lon": base_lon + random.uniform(-0.05, 0.05),
                "speed": random.uniform(20, 40),
                "heading": random.uniform(0, 360)
            })
            
        # Hostile units
        for i in range(2):
            self.units.append({
                "id": f"H-{i+1}",
                "type": "hostile",
                "lat": base_lat + random.uniform(0.1, 0.2), # Start further away
                "lon": base_lon + random.uniform(0.1, 0.2),
                "speed": random.uniform(30, 50),
                "heading": 225 # Moving towards center
            })

    async def run(self):
        while True:
            current_time = time.time()
            dt = current_time - self.last_update
            self.last_update = current_time

            # Update positions
            for unit in self.units:
                # Hostiles move towards center (11.62, 92.72)
                if unit["type"] == "hostile":
                    target_lat, target_lon = 11.6233, 92.7265
                    if unit["lat"] > target_lat: unit["lat"] -= 0.0001 * unit["speed"] * dt
                    else: unit["lat"] += 0.0001 * unit["speed"] * dt
                    
                    if unit["lon"] > target_lon: unit["lon"] -= 0.0001 * unit["speed"] * dt
                    else: unit["lon"] += 0.0001 * unit["speed"] * dt
                else:
                    # Friendlies patrol randomly
                    unit["lat"] += 0.00005 * unit["speed"] * dt * (1 if random.random() > 0.5 else -1)
                    unit["lon"] += 0.00005 * unit["speed"] * dt * (1 if random.random() > 0.5 else -1)

            # Replenish hostiles if they are cleared (Execute command)
            hostiles = [u for u in self.units if u["type"] == "hostile"]
            if len(hostiles) < 2:
                self.units.append({
                    "id": f"H-NEW-{random.randint(100, 999)}",
                    "type": "hostile",
                    "lat": 11.6233 + random.uniform(0.1, 0.15),
                    "lon": 92.7265 + random.uniform(0.1, 0.15),
                    "speed": random.uniform(30, 50),
                    "heading": 225
                })

            await asyncio.sleep(1)

    def get_state(self) -> Dict:
        return {
            "units": self.units,
            "is_jamming": self.is_jamming,
            "timestamp": time.time(),
            # Send alert if hostile is close
            "alerts": self._generate_alerts()
        }

    def _generate_alerts(self) -> List[Dict]:
        alerts = []
        center_lat, center_lon = 11.6233, 92.7265
        for unit in self.units:
            if unit["type"] == "hostile":
                dist = ((unit["lat"] - center_lat)**2 + (unit["lon"] - center_lon)**2)**0.5
                if dist < 0.1: # Proximity threshold
                    alerts.append({
                        "id": f"ALERT-{unit['id']}",
                        "severity": "CRITICAL",
                        "message": f"Hostile Unit {unit['id']} breached primary exclusion zone!",
                        "timestamp": time.time()
                    })
        return alerts

    def handle_command(self, command: str):
        if command == "EXECUTE":
            # Clear all hostiles
            self.units = [u for u in self.units if u["type"] != "hostile"]
            print(f"SIMULATOR: Neutralized all hostile units.")
        elif command == "ABORT":
            print(f"SIMULATOR: Engagement aborted. Standing down.")
        elif command == "TOGGLE_JAMMING":
            self.is_jamming = not self.is_jamming
            print(f"SIMULATOR: GPS Jamming {'ACTIVE' if self.is_jamming else 'INACTIVE'}")
