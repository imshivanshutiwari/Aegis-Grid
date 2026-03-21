"""Domain models establishing fundamental types across boundaries."""
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class Role(str, Enum):
    """User access control roles."""
    OBSERVER = "OBSERVER"
    ANALYST = "ANALYST"
    COMMANDER = "COMMANDER"
    SUPERADMIN = "SUPERADMIN"

class ThreatLevel(str, Enum):
    """Enumeration for entity threat evaluation."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class UnitType(str, Enum):
    """Types of combatants or entities."""
    FRIENDLY = "FRIENDLY"
    HOSTILE = "HOSTILE"
    UNKNOWN = "UNKNOWN"

class Coordinate(BaseModel):
    """Geospatial point container."""
    lon: float
    lat: float

class UnitState(BaseModel):
    """Stateful representation of an entity in the simulation."""
    id: UUID = Field(default_factory=uuid4)
    unit_type: UnitType
    position: Coordinate
    velocity: Coordinate = Field(default_factory=lambda: Coordinate(lon=0, lat=0))
    heading: float = 0.0
    threat_level: Optional[ThreatLevel] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
