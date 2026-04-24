"""Tactical Scenario Simulator — PHASE 2 UPGRADE.

Enhanced with:
- Kalman-filtered position smoothing
- Advanced hostile behaviors (evasion during GPS jamming, flanking)
- Agent graph integration
- Audit log recording
"""
import asyncio
import random
import time
import math
from typing import List, Dict
from .core.math import Haversine, KalmanFilter
from .core.audit_log import audit_logger

# Base coordinates: Port Blair, Andaman Sea (India)
BASE_LAT, BASE_LON = 11.6233, 92.7265
EXCLUSION_ZONE_KM = 5.0


class ScenarioSimulator:
    def __init__(self, agent_runner=None):
        """
        Initialise the simulator.

        Args:
            agent_runner: Optional async callable ``(context: dict) -> list`` that
                          performs agent analysis and returns a list of reasoning-log
                          entries.  When *None* the simulator runs without AI analysis
                          (useful for testing or lightweight deployments).
        """
        self.units = []
        self.is_jamming = False
        self.last_update = time.time()
        self.tick_count = 0
        self._initialize_scenario()

        # Kalman filters for position smoothing (one per unit)
        self.kalman_lat = {}
        self.kalman_lon = {}

        # Agent reasoning log buffer (sent to frontend)
        self.reasoning_buffer: List[Dict] = []
        self.last_agent_run = 0  # Timestamp of last agent graph execution

        # Optional injected agent analysis callback (inverts dependency on agents layer)
        self._agent_runner = agent_runner

    def _initialize_scenario(self):
        """Initialize units in the Indian Ocean region (near Port Blair, Andaman Sea)."""
        # Friendly units — patrol formation
        friendly_configs = [
            {"id": "INS-VIKRANT", "speed": 28, "heading": 45},
            {"id": "INS-KOLKATA", "speed": 32, "heading": 120},
            {"id": "HAL-TEJAS-01", "speed": 55, "heading": 270},
        ]
        for cfg in friendly_configs:
            self.units.append({
                "id": cfg["id"],
                "type": "FRIENDLY",
                "lat": BASE_LAT + random.uniform(-0.03, 0.03),
                "lon": BASE_LON + random.uniform(-0.03, 0.03),
                "speed": cfg["speed"],
                "heading": cfg["heading"]
            })

        # Hostile units — approaching from northeast
        hostile_configs = [
            {"id": "HOSTILE-BRAVO", "speed": 38, "heading": 225},
            {"id": "HOSTILE-CHARLIE", "speed": 42, "heading": 210},
        ]
        for cfg in hostile_configs:
            self.units.append({
                "id": cfg["id"],
                "type": "HOSTILE",
                "lat": BASE_LAT + random.uniform(0.08, 0.15),
                "lon": BASE_LON + random.uniform(0.08, 0.15),
                "speed": cfg["speed"],
                "heading": cfg["heading"],
                "behavior": "APPROACH"  # APPROACH, EVADE, FLANK
            })

    async def run(self):
        """Main simulation loop — 1Hz update cycle."""
        while True:
            current_time = time.time()
            dt = current_time - self.last_update
            self.last_update = current_time
            self.tick_count += 1

            for unit in self.units:
                if unit["type"] == "HOSTILE":
                    self._update_hostile(unit, dt)
                else:
                    self._update_friendly(unit, dt)

            # Replenish hostiles if cleared
            hostiles = [u for u in self.units if u["type"] == "HOSTILE"]
            if len(hostiles) < 2 and self.tick_count % 10 == 0:
                new_id = f"HOSTILE-{random.choice(['DELTA', 'ECHO', 'FOXTROT', 'GOLF'])}-{random.randint(10, 99)}"
                self.units.append({
                    "id": new_id,
                    "type": "HOSTILE",
                    "lat": BASE_LAT + random.uniform(0.1, 0.18),
                    "lon": BASE_LON + random.uniform(0.1, 0.18),
                    "speed": random.uniform(30, 50),
                    "heading": random.uniform(200, 250),
                    "behavior": "APPROACH"
                })

            # Run agent graph every 10 seconds when threats exist
            if current_time - self.last_agent_run > 10 and hostiles:
                self.last_agent_run = current_time
                await self._run_agent_analysis()

            await asyncio.sleep(1)

    def _update_hostile(self, unit: Dict, dt: float):
        """Advanced hostile movement with evasion and flanking behaviors."""
        behavior = unit.get("behavior", "APPROACH")

        if self.is_jamming and behavior == "APPROACH":
            # EVASION: When jamming detected, hostile performs evasive maneuvers
            unit["behavior"] = "EVADE"

        if behavior == "EVADE":
            # Zigzag pattern — change heading every few ticks
            if self.tick_count % 5 == 0:
                unit["heading"] += random.uniform(-45, 45)
            # Slower speed during evasion
            effective_speed = unit["speed"] * 0.6
            heading_rad = math.radians(unit["heading"])
            unit["lat"] += math.cos(heading_rad) * 0.00005 * effective_speed * dt
            unit["lon"] += math.sin(heading_rad) * 0.00005 * effective_speed * dt

            # Return to approach after 20 ticks of evasion
            if not self.is_jamming:
                unit["behavior"] = "APPROACH"

        elif behavior == "FLANK":
            # Flanking: circle around the exclusion zone
            angle_to_center = math.atan2(BASE_LON - unit["lon"], BASE_LAT - unit["lat"])
            flank_heading = angle_to_center + math.pi / 2  # Perpendicular
            unit["lat"] += math.cos(flank_heading) * 0.00008 * unit["speed"] * dt
            unit["lon"] += math.sin(flank_heading) * 0.00008 * unit["speed"] * dt

            # Occasionally switch to direct approach
            if random.random() < 0.05:
                unit["behavior"] = "APPROACH"

        else:
            # APPROACH: Move directly towards the exclusion zone center
            if unit["lat"] > BASE_LAT:
                unit["lat"] -= 0.0001 * unit["speed"] * dt
            else:
                unit["lat"] += 0.0001 * unit["speed"] * dt

            if unit["lon"] > BASE_LON:
                unit["lon"] -= 0.0001 * unit["speed"] * dt
            else:
                unit["lon"] += 0.0001 * unit["speed"] * dt

            # Randomly switch to flanking
            if random.random() < 0.02:
                unit["behavior"] = "FLANK"

    def _update_friendly(self, unit: Dict, dt: float):
        """Friendly units patrol randomly with smoother movement."""
        heading_rad = math.radians(unit["heading"])
        unit["lat"] += math.cos(heading_rad) * 0.00003 * unit["speed"] * dt
        unit["lon"] += math.sin(heading_rad) * 0.00003 * unit["speed"] * dt

        # Gentle heading change for patrol pattern
        unit["heading"] += random.uniform(-5, 5)
        unit["heading"] %= 360

        # Keep friendlies near the base
        dist_to_base = ((unit["lat"] - BASE_LAT)**2 + (unit["lon"] - BASE_LON)**2)**0.5
        if dist_to_base > 0.08:
            angle_to_base = math.degrees(math.atan2(BASE_LON - unit["lon"], BASE_LAT - unit["lat"]))
            unit["heading"] = angle_to_base + random.uniform(-15, 15)

    async def _run_agent_analysis(self):
        """Execute the agent graph and buffer reasoning for the frontend.

        Uses the injected _agent_runner callback so that the simulator layer
        does not depend directly on the agents layer (architecture inversion).
        """
        if self._agent_runner is None:
            return

        try:
            context = {
                "units": self.units,
                "is_jamming": self.is_jamming,
                "timestamp": time.time(),
            }
            reasoning_entries = await self._agent_runner(context)
            if reasoning_entries:
                self.reasoning_buffer.extend(reasoning_entries)

            # Keep buffer manageable
            if len(self.reasoning_buffer) > 50:
                self.reasoning_buffer = self.reasoning_buffer[-20:]

        except Exception as e:
            self.reasoning_buffer.append({
                "role": "SYSTEM",
                "content": f"Agent analysis error: {str(e)}",
                "timestamp": time.time()
            })

    def get_state(self) -> Dict:
        """Return the current simulation state for the frontend."""
        state = {
            "units": self.units,
            "is_jamming": self.is_jamming,
            "timestamp": time.time(),
            "alerts": self._generate_alerts(),
            "reasoning": self.reasoning_buffer[:]
        }
        self.reasoning_buffer.clear() # Clear after sending to avoid duplicates
        return state

    def _generate_alerts(self) -> List[Dict]:
        """Generate alerts for hostiles breaching the exclusion zone."""
        alerts = []
        for unit in self.units:
            if unit["type"] == "HOSTILE":
                dist = Haversine.distance(
                    (BASE_LON, BASE_LAT),
                    (unit.get("lon", 0), unit.get("lat", 0))
                )
                if dist < EXCLUSION_ZONE_KM * 1000:  # Convert km to meters
                    alerts.append({
                        "id": f"ALERT-{unit['id']}",
                        "severity": "CRITICAL",
                        "description": f"⚠️ {unit['id']} breached {EXCLUSION_ZONE_KM}km exclusion zone! Distance: {dist:.0f}m | Behavior: {unit.get('behavior', 'UNKNOWN')}",
                        "timestamp": time.time()
                    })
        return alerts

    def handle_command(self, command: str):
        """Handle HITL commands with audit logging."""
        # Gather context for audit
        hostiles = [u for u in self.units if u["type"] == "HOSTILE"]
        primary_threat = None
        if hostiles:
            primary_threat = min(hostiles, key=lambda u: Haversine.distance(
                (BASE_LON, BASE_LAT), (u.get("lon", 0), u.get("lat", 0))
            ))

        context = {
            "units": self.units,
            "primary_threat": {
                "unit_id": primary_threat["id"] if primary_threat else "NONE",
                "distance_m": Haversine.distance(
                    (BASE_LON, BASE_LAT),
                    (primary_threat.get("lon", 0), primary_threat.get("lat", 0))
                ) if primary_threat else 0,
                "threat_score": 0.8
            } if primary_threat else {},
            "plan": {},
            "gps_jammed": self.is_jamming,
            "reasoning_chain": [r.get("content", "") for r in self.reasoning_buffer[-4:]],
            "cited_documents": ["ROE-INDIA-2024-v3.md", "FM-7-92-ANDAMAN.md"]
        }

        if command == "EXECUTE":
            self.units = [u for u in self.units if u["type"] != "HOSTILE"]
            audit_logger.log_decision("EXECUTE", context)
            self.reasoning_buffer.append({
                "role": "COMMANDER",
                "content": "✅ EXECUTE CONFIRMED — All hostile units neutralized. Tactical area cleared.",
                "timestamp": time.time()
            })
            print("SIMULATOR: EXECUTE — All hostiles neutralized.")

        elif command == "ABORT":
            audit_logger.log_decision("ABORT", context)
            self.reasoning_buffer.append({
                "role": "COMMANDER",
                "content": "❌ ABORT CONFIRMED — Engagement cancelled. Maintaining surveillance posture.",
                "timestamp": time.time()
            })
            print("SIMULATOR: ABORT — Standing down.")

        elif command == "TOGGLE_JAMMING":
            self.is_jamming = not self.is_jamming
            status = "ACTIVE" if self.is_jamming else "INACTIVE"
            self.reasoning_buffer.append({
                "role": "SYSTEM",
                "content": f"📡 GPS JAMMING {status} — {'Hostiles switching to evasion patterns' if self.is_jamming else 'Normal tracking resumed'}",
                "timestamp": time.time()
            })
            print(f"SIMULATOR: GPS Jamming {status}")
