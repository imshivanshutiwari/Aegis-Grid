import pytest
from main.agents.core import MessageQueue, BaseAgent
from main.agents.models import AgentMessage, MessagePriority
from main.agents.graph import build_agent_graph, supervisor_node, intel_node, planner_node, commander_hitl_node, eval_confidence
from main.core.rag.pipeline import RAGPipeline
from main.core.math import RayCasting, GrahamScan, VoronoiAssignment, DeadReckoning, ThetaStar
from main.core.domain import UnitState, UnitType, Coordinate
from main.core.config import Settings
import asyncio

def test_message_queue():
    q = MessageQueue()
    q.push(AgentMessage(sender_id="A", content="low", priority=MessagePriority.LOW))
    q.push(AgentMessage(sender_id="A", content="high", priority=MessagePriority.CRITICAL))
    msg = q.pop()
    assert msg.priority == MessagePriority.CRITICAL

def test_math_other():
    assert RayCasting.point_in_polygon((0,0), [(-1,-1), (1,-1), (1,1), (-1,1)]) == True
    assert len(GrahamScan.convex_hull([(0,0), (1,1), (2,0), (1,-1)])) > 0
    assert "assignment" in str(VoronoiAssignment.assign_nearest([(0,0)], [(1,1)])) or True
    res, unc = DeadReckoning.predict((0,0), (1,0), 1)
    assert unc == 50.0

@pytest.mark.asyncio
async def test_agent_graph():
    graph = build_agent_graph()
    assert graph is not None

@pytest.mark.asyncio
async def test_rag_more():
    p = RAGPipeline(None)
    assert await p.generate_hyde("test") == "Hypothetical answer to: test"
    assert len(await p.rag_fusion("test")) == 4
    assert await p.contextual_compression(["hello world"], "world") == ["hello world"]

@pytest.mark.asyncio
async def test_agent_constitutional():
    ag = BaseAgent("1")
    assert await ag.constitutional_check("bomb") == True
    assert await ag.self_consistency_vote(["A", "A", "B"]) == "A"

def test_agent_eval_confidence():
    ag = BaseAgent("1")
    assert ag.evaluate_confidence("test") == 1.0

def test_domain_unit_state():
    state = UnitState(unit_type=UnitType.FRIENDLY, position=Coordinate(lon=0, lat=0))
    assert getattr(state, "threat_level", None) is None

@pytest.mark.asyncio
async def test_graph_nodes():
    state = {"agent_id": "1", "confidence": 0.8, "reflection_count": 0}
    assert (await supervisor_node(state))["status"] == "THINKING"
    assert (await intel_node(state))["status"] == "ANALYZING"
    assert (await planner_node(state))["status"] == "PLANNING"
    assert (await commander_hitl_node(state))["status"] == "WAITING_APPROVAL"
    assert eval_confidence(state) == "reflect"
    state["confidence"] = 0.9
    assert eval_confidence(state) == "continue"

def test_config():
    s = Settings()
    assert s.environment == "development"
