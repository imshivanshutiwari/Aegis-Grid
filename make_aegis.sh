mkdir -p aegis-grid/backend/main/agents \
aegis-grid/backend/main/core \
aegis-grid/backend/main/database \
aegis-grid/backend/main/api \
aegis-grid/backend/tests \
aegis-grid/frontend/src/components \
aegis-grid/data/mock_doctrines \
aegis-grid/.github/workflows \
aegis-grid/deployment/grafana \
aegis-grid/deployment/prometheus

cat << 'INNER_EOF' > aegis-grid/README.md
# Project Aegis-Grid
Aegis-Grid (Tactical Multi-Agent Geospatial Intelligence & Response System)
INNER_EOF

cat << 'INNER_EOF' > aegis-grid/backend/main/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import List
class Settings(BaseSettings):
    environment: str = "development"
    jwt_secret: SecretStr = SecretStr("supersecretdefensekey_change_in_prod")
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aegis"
    qdrant_url: str = "http://localhost:6333"
    ollama_url: str = "http://localhost:11434"
    cors_origins: List[str] = ["http://localhost:3000"]
    MAX_WS_CONNECTIONS: int = 1000
    GPS_JAMMED_NOISE_SIGMA: float = 50.0
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
settings = Settings()
INNER_EOF

cat << 'INNER_EOF' > aegis-grid/backend/main/core/domain.py
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
class Role(str, Enum): OBSERVER, ANALYST, COMMANDER, SUPERADMIN = "OBSERVER", "ANALYST", "COMMANDER", "SUPERADMIN"
class ThreatLevel(str, Enum): LOW, MEDIUM, HIGH, CRITICAL = "LOW", "MEDIUM", "HIGH", "CRITICAL"
class UnitType(str, Enum): FRIENDLY, HOSTILE, UNKNOWN = "FRIENDLY", "HOSTILE", "UNKNOWN"
class Coordinate(BaseModel): lon: float; lat: float
class UnitState(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    unit_type: UnitType
    position: Coordinate
    velocity: Coordinate = Field(default_factory=lambda: Coordinate(lon=0, lat=0))
    heading: float = 0.0
    threat_level: Optional[ThreatLevel] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
INNER_EOF

cat << 'INNER_EOF' > aegis-grid/backend/main/core/math.py
import math
from typing import Tuple, List, Callable
class Haversine:
    @staticmethod
    def distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        lon1, lat1 = coord1; lon2, lat2 = coord2
        R = 6371000; phi1 = math.radians(lat1); phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1); delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))
class AStar:
    @staticmethod
    def search(start: Tuple[float, float], goal: Tuple[float, float], get_neighbors: Callable, heuristic: Callable) -> List[Tuple[float, float]]:
        import heapq
        open_set = []; heapq.heappush(open_set, (0, start))
        came_from = {}; g_score = {start: 0}; f_score = {start: heuristic(start, goal)}
        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                path = []
                while current in came_from: path.append(current); current = came_from[current]
                path.append(start); path.reverse(); return path
            for neighbor in get_neighbors(current):
                tentative_g_score = g_score[current] + Haversine.distance(current, neighbor)
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current; g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    if neighbor not in [i[1] for i in open_set]: heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []
class KalmanFilter:
    def __init__(self, process_variance: float, estimated_measurement_variance: float):
        self.process_variance = process_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0; self.posteri_error_estimate = 1.0; self.is_initialized = False
    def input_latest_noisy_measurement(self, measurement: float):
        if not self.is_initialized: self.posteri_estimate = measurement; self.is_initialized = True; return
        priori_estimate = self.posteri_estimate; priori_error_estimate = self.posteri_error_estimate + self.process_variance
        blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate
    def get_latest_estimated_measurement(self) -> float: return self.posteri_estimate
class DBSCAN:
    @staticmethod
    def cluster(data: List[Tuple[float, float]], eps: float, min_pts: int) -> List[int]:
        labels = [0] * len(data); cluster_id = 0
        for i, point in enumerate(data):
            if labels[i] != 0: continue
            neighbors = [j for j, p in enumerate(data) if Haversine.distance(point, p) <= eps]
            if len(neighbors) < min_pts: labels[i] = -1; continue
            cluster_id += 1; labels[i] = cluster_id; seed_set = neighbors; seed_set.remove(i)
            while seed_set:
                current_point_idx = seed_set.pop(0)
                if labels[current_point_idx] == -1: labels[current_point_idx] = cluster_id
                if labels[current_point_idx] != 0: continue
                labels[current_point_idx] = cluster_id
                current_neighbors = [j for j, p in enumerate(data) if Haversine.distance(data[current_point_idx], p) <= eps]
                if len(current_neighbors) >= min_pts: seed_set.extend(current_neighbors)
        return labels
INNER_EOF

cat << 'INNER_EOF' > aegis-grid/backend/main/core/event_bus.py
import asyncio
from typing import Callable, Awaitable, Dict, List, Any
EventHandler = Callable[[Any], Awaitable[None]]
class EventBus:
    def __init__(self): self._subscribers: Dict[str, List[EventHandler]] = {}
    def subscribe(self, event_type: str, handler: EventHandler):
        if event_type not in self._subscribers: self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    async def publish(self, event_type: str, event_data: Any):
        if event_type in self._subscribers:
            tasks = [handler(event_data) for handler in self._subscribers[event_type]]
            await asyncio.gather(*tasks, return_exceptions=True)
event_bus = EventBus()
INNER_EOF

cat << 'INNER_EOF' > aegis-grid/backend/main/core/circuit_breaker.py
import asyncio
from typing import Callable, Any
from functools import wraps
class CircuitBreakerOpenException(Exception): pass
def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 30.0):
    def decorator(func: Callable) -> Callable:
        state = {"failures": 0, "open": False, "last_failure_time": 0.0}
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if state["open"]:
                import time
                if time.time() - state["last_failure_time"] > recovery_timeout:
                    state["open"] = False; state["failures"] = 0
                else: raise CircuitBreakerOpenException(f"Circuit {func.__name__} is OPEN")
            try: result = await func(*args, **kwargs); state["failures"] = 0; return result
            except Exception as e:
                import time
                state["failures"] += 1; state["last_failure_time"] = time.time()
                if state["failures"] >= failure_threshold: state["open"] = True
                raise e
        return wrapper
    return decorator
INNER_EOF

cat << 'INNER_EOF' > aegis-grid/backend/tests/test_math.py
import pytest
from main.core.math import Haversine, AStar, KalmanFilter, DBSCAN
def test_haversine_distance_same_point():
    point = (0.0, 0.0)
    assert Haversine.distance(point, point) == 0.0
def test_haversine_distance_known():
    london = (-0.1278, 51.5074)
    paris = (2.3522, 48.8566)
    dist = Haversine.distance(london, paris)
    assert 340000 < dist < 350000
def test_astar_search():
    def get_neighbors(node): x, y = node; return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    start = (0, 0); goal = (2, 2)
    path = AStar.search(start, goal, get_neighbors, Haversine.distance)
    assert len(path) == 5; assert path[0] == start; assert path[-1] == goal
def test_kalman_filter():
    kf = KalmanFilter(process_variance=1e-5, estimated_measurement_variance=0.1)
    kf.input_latest_noisy_measurement(10.0)
    est1 = kf.get_latest_estimated_measurement()
    kf.input_latest_noisy_measurement(10.5)
    est2 = kf.get_latest_estimated_measurement()
    assert est1 != est2
    assert 10.0 < est2 <= 10.5
def test_dbscan_clustering():
    data = [(0.0, 0.0), (0.1, 0.1), (10.0, 10.0), (10.1, 10.1)]
    eps = 25000
    labels = DBSCAN.cluster(data, eps=eps, min_pts=2)
    assert labels[0] == labels[1]
    assert labels[2] == labels[3]
    assert labels[0] != labels[2]
INNER_EOF

cat << 'INNER_EOF' > aegis-grid/backend/tests/test_circuit_breaker.py
import pytest
import asyncio
from main.core.circuit_breaker import circuit_breaker, CircuitBreakerOpenException
@pytest.mark.asyncio
async def test_circuit_breaker_success():
    @circuit_breaker(failure_threshold=2, recovery_timeout=1)
    async def dummy_call(): return "Success"
    assert await dummy_call() == "Success"
@pytest.mark.asyncio
async def test_circuit_breaker_trip():
    @circuit_breaker(failure_threshold=2, recovery_timeout=1)
    async def failing_call(): raise ValueError("Intentional Fail")
    with pytest.raises(ValueError): await failing_call()
    with pytest.raises(ValueError): await failing_call()
    with pytest.raises(CircuitBreakerOpenException): await failing_call()
INNER_EOF

cat << 'INNER_EOF' > aegis-grid/backend/tests/test_event_bus.py
import pytest
import asyncio
from main.core.event_bus import event_bus
@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    test_result = []
    async def test_handler(data): test_result.append(data)
    event_bus.subscribe("test_event", test_handler)
    await event_bus.publish("test_event", {"key": "value"})
    assert len(test_result) == 1
    assert test_result[0] == {"key": "value"}
INNER_EOF
