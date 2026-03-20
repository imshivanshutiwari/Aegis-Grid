from typing import TypedDict, Annotated, List, Dict, Any, Optional
from pydantic import BaseModel, Field
import operator

class BDI_State(BaseModel):
    """Belief-Desire-Intention State Model"""
    beliefs: Dict[str, Any] = Field(description="Current world state from PostGIS and RAG")
    desires: List[str] = Field(description="Mission objectives like 'Intercept Hostile Drone'")
    intentions: List[str] = Field(description="Selected plan from tactical planner")

class AgentState(TypedDict):
    """Global state of the agent team utilizing LangGraph."""
    threat_event: Dict[str, Any]
    bdi_state: Dict[str, Any]  # serialized BDI_State
    intel_analysis: Optional[str]
    tactical_plan: Optional[str]
    confidence_score: float
    documents_cited: List[str]
    human_approved: Optional[bool]
    messages: Annotated[List[Dict[str, Any]], operator.add]
    reflection_attempts: int
