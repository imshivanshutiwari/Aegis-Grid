# Aegis-Grid Agent Protocol

The Multi-Agent architecture is powered by LangGraph, operating under a BDI (Belief-Desire-Intention) model.

## 1. Supervisor Agent
- **Role**: Event router and state initializer.
- **Trigger**: Awakened by the WebSocket pub/sub EventBus when a `CRITICAL` threat event occurs.
- **Action**: Initializes the `BDI_State` and passes control to the Intel Analyst.

## 2. Intel Analyst Agent
- **Role**: Situational awareness and doctrine retrieval.
- **ReAct Loop**:
  - **Thought**: What rules apply to this geofenced area and threat type?
  - **Action**: Query the Advanced RAG Pipeline (Qdrant).
  - **Observation**: Retrieves semantic chunks using HyDE and RRF.
  - **Reflection**: Summarize ROE and update `beliefs` in BDI State.

## 3. Tactical Planner Agent
- **Role**: Swarm routing and interception calculations.
- **Tree of Thoughts**: Explores multiple interception routes considering GPS Jamming uncertainty.
- **Reflexion**: If confidence < 0.9, the agent reflects on its route calculation and regenerates.
- **Constitutional AI**: Checks its proposed route against the ROE injected by the Intel Analyst.

## 4. Human-in-the-Loop (HITL) Node
- **Role**: Ethical and Commander override.
- **Action**: Pauses LangGraph execution, saves state via SQLite Checkpointing, and waits for a boolean flag over WebSocket to `execute` or `abort`.
