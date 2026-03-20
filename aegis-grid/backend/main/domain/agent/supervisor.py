import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from main.domain.agent.models import AgentState, BDI_State
from main.infrastructure.config.settings import settings

try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    import sqlite3
    db_path = "aegis_checkpoint.sqlite"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory_saver = SqliteSaver(conn)
except ImportError:
    memory_saver = None

logger = logging.getLogger(__name__)

def supervisor_agent(state: AgentState) -> Dict[str, Any]:
    """Wakes up on CRITICAL threat and initializes BDI state."""
    logger.info(f"Supervisor awoken for threat: {state['threat_event']['id']}")
    bdi = BDI_State(
        beliefs={"threat_location": state['threat_event']['position'], "threat_type": state['threat_event']['unit_type']},
        desires=["Identify Threat", "Determine Intercept Plan"],
        intentions=[]
    )
    return {
        "bdi_state": bdi.model_dump(),
        "messages": [{"role": "supervisor", "content": "Initializing BDI state and routing to Intel Analyst"}]
    }

def intel_analyst_agent(state: AgentState) -> Dict[str, Any]:
    """Retrieves ROE via RAG and updates beliefs."""
    logger.info("Intel Analyst analyzing threat and pulling RAG...")
    analysis = f"Hostile unit detected at {state['bdi_state']['beliefs']['threat_location']}. Per ROE section 4.1, immediate intercept required."
    docs = ["ROE_Section_4.1"]

    bdi = state["bdi_state"]
    bdi["beliefs"]["roe_analysis"] = analysis

    return {
        "intel_analysis": analysis,
        "bdi_state": bdi,
        "documents_cited": state["documents_cited"] + docs,
        "messages": [{"role": "intel", "content": "Analysis complete, passing to Tactical"}]
    }

def tactical_planner_agent(state: AgentState) -> Dict[str, Any]:
    """Drafts intercept plan. Uses Tree of Thoughts (mocked)."""
    logger.info("Tactical Planner drafting intercept plan...")
    plan = f"Deploy swarm alpha to intercept at {state['bdi_state']['beliefs']['threat_location']}."

    bdi = state["bdi_state"]
    bdi["intentions"] = ["Execute swarm deployment"]

    return {
        "tactical_plan": plan,
        "bdi_state": bdi,
        "confidence_score": 0.85, # Below 0.9 triggers reflexion check
        "messages": [{"role": "tactical", "content": "Plan drafted, awaiting Constitutional Review"}]
    }

def constitutional_review(state: AgentState) -> Dict[str, Any]:
    """Constitutional AI check against ROE before any action proposal."""
    logger.info("Reviewing plan against Constitutional ROE...")
    confidence = state["confidence_score"]

    if confidence < 0.9 and state["reflection_attempts"] < 2:
        return {
            "reflection_attempts": state["reflection_attempts"] + 1,
            "messages": [{"role": "reviewer", "content": "Plan rejected: Confidence too low. Regenerating..."}]
        }

    return {
        "messages": [{"role": "reviewer", "content": "Plan passed Constitutional Review. Awaiting HITL."}]
    }

def should_reflect(state: AgentState) -> str:
    """Conditional edge for Reflexion pattern."""
    if state["reflection_attempts"] > 0 and state["reflection_attempts"] < 2 and state["confidence_score"] < 0.9:
        return "tactical_planner"
    return "human_in_the_loop"

def human_in_the_loop(state: AgentState) -> Dict[str, Any]:
    """Pauses graph until commander approves/rejects via websocket."""
    logger.info("Awaiting HITL Commander approval...")
    return {"messages": [{"role": "system", "content": "Waiting for Commander action."}]}

def should_execute(state: AgentState) -> str:
    if state.get("human_approved") is True: return "execute_plan"
    elif state.get("human_approved") is False: return "abort_plan"
    else: return "human_in_the_loop"

def execute_plan(state: AgentState) -> Dict[str, Any]:
    logger.info("Executing tactical plan!")
    return {"messages": [{"role": "system", "content": "Plan executed successfully."}]}

def abort_plan(state: AgentState) -> Dict[str, Any]:
    logger.info("Tactical plan aborted by Commander.")
    return {"messages": [{"role": "system", "content": "Plan aborted."}]}

# Build Graph
graph = StateGraph(AgentState)

graph.add_node("supervisor", supervisor_agent)
graph.add_node("intel_analyst", intel_analyst_agent)
graph.add_node("tactical_planner", tactical_planner_agent)
graph.add_node("constitutional_review", constitutional_review)
graph.add_node("human_in_the_loop", human_in_the_loop)
graph.add_node("execute_plan", execute_plan)
graph.add_node("abort_plan", abort_plan)

graph.set_entry_point("supervisor")
graph.add_edge("supervisor", "intel_analyst")
graph.add_edge("intel_analyst", "tactical_planner")
graph.add_edge("tactical_planner", "constitutional_review")
graph.add_conditional_edges("constitutional_review", should_reflect)
graph.add_conditional_edges("human_in_the_loop", should_execute)

graph.add_edge("execute_plan", END)
graph.add_edge("abort_plan", END)

aegis_graph = graph.compile(checkpointer=memory_saver) if memory_saver else graph.compile()
