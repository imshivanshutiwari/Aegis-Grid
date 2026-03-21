"""LangGraph execution layer defining the Multi-Agent system."""
from typing import Dict, Any, TypedDict, Callable, Awaitable, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import asyncio
from .models import AgentState, AgentRole, AgentMessage, MessagePriority

async def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Node representing the Supervisor Agent."""
    import logging; logging.info(f"Supervisor evaluating state: {state['agent_id']}")
    return {"status": "THINKING", "confidence": 0.9}

async def intel_node(state: AgentState) -> Dict[str, Any]:
    """Node representing the Intel Analyst Agent."""
    return {"status": "ANALYZING", "confidence": 0.85}

async def planner_node(state: AgentState) -> Dict[str, Any]:
    """Node representing the Tactical Planner Agent."""
    return {"status": "PLANNING", "confidence": 0.95}

async def commander_hitl_node(state: AgentState) -> Dict[str, Any]:
    """Node representing the Human-In-The-Loop commander step."""
    import logging; logging.info("Pausing graph for Commander Human-in-the-Loop approval via WebSocket...")
    return {"status": "WAITING_APPROVAL"}

def eval_confidence(state: AgentState) -> str:
    """Conditional edge logic evaluating agent confidence (Tree of Thoughts/Reflexion)."""
    if state["confidence"] < 0.85 and state["reflection_count"] < 3:
        return "reflect"
    return "continue"

def build_agent_graph():
    """Construct and compile the LangGraph StateGraph instance."""
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("intel_analyst", intel_node)
    graph.add_node("tactical_planner", planner_node)
    graph.add_node("commander_hitl", commander_hitl_node)
    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor", "intel_analyst")
    graph.add_edge("intel_analyst", "tactical_planner")
    graph.add_conditional_edges(
        "tactical_planner",
        eval_confidence,
        {
            "reflect": "intel_analyst",
            "continue": "commander_hitl"
        }
    )
    graph.add_edge("commander_hitl", END)
    conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
    saver = SqliteSaver(conn)
    return graph.compile(checkpointer=saver)

async def parallel_execution(agents: List[Callable[[Any], Awaitable[Any]]], context: Any):
    """Execute a list of agent functions in parallel via asyncio."""
    tasks = [agent(context) for agent in agents]
    return await asyncio.gather(*tasks)
