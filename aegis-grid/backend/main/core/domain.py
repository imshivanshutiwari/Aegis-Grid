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
