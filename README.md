# Aegis-Grid 🦅
**Tactical Multi-Agent Geospatial Intelligence & Response System**

![Aegis Grid Banner](https://via.placeholder.com/1200x400.png?text=AEGIS-GRID+C2+ARCHITECTURE)

## Overview
Aegis-Grid is a conceptual, air-gapped Command and Control (C2) system designed for the modern contested battlespace. It fuses real-time geospatial intelligence with deterministic, stateful Multi-Agent AI (LangGraph) and local Retrieval-Augmented Generation (RAG). 

When a hostile entity breaches a geofenced zone, Aegis-Grid autonomously evaluates the threat against ingested tactical doctrines (ROE) and proposes a multi-domain response plan (e.g., routing a drone swarm) to a Human-in-the-Loop (HITL) commander.

### Key Capabilities
*   **Geospatial Telemetry Ingestion:** Simulates streaming hundreds of moving units (Friendlies, Hostiles, Unknowns) via WebSockets to a WebGL-accelerated `deck.gl` map.
*   **Multi-Agent Orchestration:** Uses `LangGraph` to coordinate a Supervisor, an Intel Analyst, and a Tactical Planner agent.
*   **Zero-Trust Edge RAG:** Connects to a local `Qdrant` vector database to query Markdown-based Rules of Engagement (ROE) and Field Manuals.
*   **Explainable AI (XAI):** Every reasoning step the LLM takes is logged and visually mapped to the specific RAG document it cited.
*   **Simulated GPS Denial:** Toggles degrade location accuracy, forcing agents to switch from precise routing to probabilistic area-search routing.

## Technology Stack
*   **Backend:** Python 3.11, FastAPI, WebSockets, LangChain, LangGraph
*   **Frontend:** React (Vite), Deck.gl, MapboxGL, TailwindCSS
*   **Databases:** PostGIS (Spatial), Qdrant (Vector/RAG)
*   **Deployment:** Docker, Docker Compose

## Architecture
```text
[ Tactical Edge / Contested Zone ]
                                                               
+-------------------+        +-----------------------------------+        +--------------------+
| Drone/Radar Feeds | -----> | FastAPI Ingestion (WebSockets)    | -----> | PostGIS (Location) |
+-------------------+        +-----------------------------------+        +--------------------+
                                      |                                            |
                                      v                                            v
                             +-----------------------------------+        +--------------------+
                             | LangGraph Supervisor Agent        | <----- | Qdrant (Vector DB) |
                             | (Threat Evaluator & Dispatcher)   |        | (Stores ROE, Docs) |
                             +-----------------------------------+        +--------------------+
                                      |              |
                    +-----------------+              +-----------------+
                    v                                                  v
+-----------------------------------+              +-----------------------------------+
| Intel Analyst Agent (Local LLM)   |              | Tactical Planner Agent (Local LLM)|
| Synthesizes threat & pulls RAG    |              | Drafts evasion/intercept routes   |
+-----------------------------------+              +-----------------------------------+
                    \                                                  /
                     \---> +------------------------------------+ <---/
                           | C2 Dashboard (React + Deck.gl Map) |
                           | Live Visualization & Approvals     |
                           +------------------------------------+
```

## Quick Start (Docker Compose)
The easiest way to spin up the entire Aegis-Grid stack (Backend, Frontend, PostGIS, Qdrant) is via Docker Compose.

### Prerequisites
*   Docker & Docker Compose installed
*   An LLM provider API key (OpenAI for testing, or Ollama/LocalAI URL for true air-gapped deployment).

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/imshivanshutiwari/Aegis-Grid.git
   cd Aegis-Grid
   ```
2. Create a `.env` file in the root directory:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   # Or for local inference:
   # OPENAI_API_BASE=http://host.docker.internal:11434/v1
   ```
3. Build and launch the stack:
   ```bash
   docker-compose up --build
   ```
4. Access the C2 Dashboard:
   Navigate to `http://localhost:5173` in your browser.
5. Access the API Documentation:
   Navigate to `http://localhost:8000/docs`.

## Local Development (Without Docker)
### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
*(Requires PostGIS on port 5432 and Qdrant on port 6333)*

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Testing
Run the Pytest suite for the backend:
```bash
cd backend
pytest tests/ -v
```

## Disclaimer
This project is a conceptual software architecture demonstration. It is not classified, nor is it intended for actual kinetic military operations without extensive hardware integration, ruggedization, and rigorous Authority to Operate (ATO) compliance testing.