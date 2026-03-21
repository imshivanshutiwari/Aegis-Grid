# Aegis-Grid Agents Documentation

This system relies on a multi-agent architecture powered by LangGraph. Each agent utilizes a BDI (Belief-Desire-Intention) model, ReAct loop, Tree of Thoughts, and Reflexion patterns.

## 1. Supervisor Agent
- **Role:** Evaluates incoming threats and coordinates other agents.
- **Responsibilities:**
  - Maintains a global view of the battlespace.
  - Triggers the Intel Analyst or Tactical Planner based on threat levels.
  - Implements the Saga Pattern for distributed transactions.

## 2. Intel Analyst Agent
- **Role:** Synthesizes threat data and retrieves relevant doctrine via RAG.
- **Responsibilities:**
  - Queries the Qdrant vector database using Hybrid Search, HyDE, and RAG Fusion.
  - Evaluates threats against the Constitutional AI rules (Rules of Engagement).
  - Provides cited documents and reasoning chains.

## 3. Tactical Planner Agent
- **Role:** Drafts evasion or intercept routes.
- **Responsibilities:**
  - Utilizes geospatial algorithms (A*, Theta*, Voronoi, DBSCAN).
  - Handles GPS-denied environments using Dead Reckoning and uncertainty ellipses.
  - Proposes response plans to the HITL Commander.
