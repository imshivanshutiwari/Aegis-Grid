import logging
from typing import Dict, Any, Optional
from core.simulator import generate_fhss, generate_bpsk, generate_qam
from agents.analyst_agent import AnalystAgent
from agents.tactical_agent import TacticalAgent
from agents.elint_agent import ELINTAgent
from memory.vector_store import VectorStoreClient
from memory.knowledge_loader import KnowledgeLoader
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from langgraph.graph import StateGraph, END
from typing import TypedDict
import os

class AgentState(TypedDict):
    """
    Typed dictionary representing the state of the LangGraph orchestrator.
    """
    input_data: str
    signal: Any
    signal_params: Dict[str, Any]
    perception: Dict[str, Any]
    action: Dict[str, Any]

def parse_input(state: AgentState) -> AgentState:
    """
    Parses the initial input data and generates the corresponding signal.

    Args:
        state (AgentState): The current state.

    Returns:
        AgentState: The updated state with the generated signal.
    """
    logger.info("Parsing input data...")
    try:
        data = json.loads(state["input_data"])
        mod_type = data.get("type", "BPSK")
        length = data.get("length", 1024)
        snr = data.get("snr", 10.0)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON input, using default BPSK simulation.")
        mod_type, length, snr = "BPSK", 1024, 10.0

    if mod_type == "FHSS":
        signal = generate_fhss(length, snr)
    elif mod_type == "QAM":
        signal = generate_qam(length, snr)
    else:
        signal = generate_bpsk(length, snr)

    state["signal"] = signal
    state["signal_params"] = {"type": mod_type, "length": length, "snr": snr}
    return state

def run_analyst(state: AgentState) -> AgentState:
    """
    Runs the Analyst Agent to analyze the generated signal.

    Args:
        state (AgentState): The current state.

    Returns:
        AgentState: The updated state with the perception dictionary.
    """
    logger.info("Running Analyst Agent...")
    analyst = AnalystAgent()
    state["perception"] = analyst.analyze_signal(state["signal"])
    return state

def run_elint(state: AgentState) -> AgentState:
    """
    Runs the ELINT Agent to contextualize the analyzed signal.

    Args:
        state (AgentState): The current state.

    Returns:
        AgentState: The updated state with additional contextual information.
    """
    logger.info("Running ELINT Agent...")
    qdrant_host = os.environ.get("QDRANT_HOST", "qdrant-server")
    qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))
    qdrant_client = VectorStoreClient(qdrant_host, qdrant_port)
    elint_agent = ELINTAgent(qdrant_client)

    context = elint_agent.contextualize_signal(state["perception"])
    state["perception"].update(context)
    return state

def run_tactical(state: AgentState) -> AgentState:
    """
    Runs the Tactical Agent to determine countermeasures.

    Args:
        state (AgentState): The current state.

    Returns:
        AgentState: The updated state with the chosen action.
    """
    logger.info("Running Tactical Agent...")
    roe = ["Do not jam friendly signals", "Prioritize FHSS jamming"]
    tactical_agent = TacticalAgent(roe)
    state["action"] = tactical_agent.determine_countermeasure(state["perception"])
    return state

def build_graph() -> StateGraph:
    """
    Builds the LangGraph orchestrator graph.

    Returns:
        StateGraph: The compiled state graph workflow.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("parse", parse_input)
    workflow.add_node("analyst", run_analyst)
    workflow.add_node("elint", run_elint)
    workflow.add_node("tactical", run_tactical)

    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "analyst")
    workflow.add_edge("analyst", "elint")
    workflow.add_edge("elint", "tactical")
    workflow.add_edge("tactical", END)

    return workflow.compile()

def run_orchestrator(input_data: str) -> Dict[str, Any]:
    """
    Main LangGraph orchestrator loop.
    Generates a synthetic signal, analyzes it, retrieves EOB context,
    and determines tactical countermeasures.

    Args:
        input_data (str): JSON string representing incoming request or sensor data.

    Returns:
        Dict[str, Any]: Complete orchestration result.
    """
    logger.info("Starting Orchestrator Loop via LangGraph")
    app = build_graph()
    initial_state = AgentState(
        input_data=input_data,
        signal=None,
        signal_params={},
        perception={},
        action={}
    )
    result = app.invoke(initial_state)

    return {
        "status": "success",
        "signal_parameters": result["signal_params"],
        "perception": result["perception"],
        "action": result["action"]
    }
