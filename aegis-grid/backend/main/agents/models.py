"""Pydantic schemas and TypedDict definitions for Agents."""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field

class AgentRole(str, Enum):
    """The type of operational role an agent fills."""
    SUPERVISOR = "SUPERVISOR"
    INTEL_ANALYST = "INTEL_ANALYST"
    TACTICAL_PLANNER = "TACTICAL_PLANNER"

class MessagePriority(str, Enum):
    """Message handling priorities."""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AgentMessage(BaseModel):
    """Schema for messages passed between agents and the C2 bus."""
    correlation_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender_id: str
    recipient_id: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    content: Any
    confidence_score: float = 1.0
    reasoning_chain: List[str] = Field(default_factory=list)
    cited_documents: List[str] = Field(default_factory=list)

class BDIMemory(TypedDict):
    """Beliefs, Desires, Intentions model schema."""
    beliefs: Dict[str, Any]
    desires: List[str]
    intentions: List[str]

class MemoryLayer(TypedDict):
    """Four-layer memory structure: sensory, working, episodic, semantic."""
    sensory_buffer: List[Any]
    working_memory: Dict[str, Any]
    episodic_memory: List[Any]
    semantic_memory: Dict[str, Any]

class AgentState(TypedDict):
    """The main TypedDict state object used by LangGraph."""
    agent_id: str
    role: AgentRole
    messages: List[AgentMessage]
    bdi: BDIMemory
    memory: MemoryLayer
    current_plan: Optional[Dict[str, Any]]
    confidence: float
    reflection_count: int
    status: str
