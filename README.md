# Aegis-Grid: Tactical Multi-Agent Geospatial Intelligence & Response System

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
*   **Backend:** Python 3.12, FastAPI, WebSockets, LangChain, LangGraph
*   **Frontend:** React (Vite), Deck.gl, MapboxGL, TailwindCSS, Zustand, React Query
*   **Databases:** PostGIS (Spatial), Qdrant (Vector/RAG), SQLite (Checkpointing)
*   **Deployment:** Docker, Docker Compose, GitHub Actions, Prometheus, Grafana

## Architecture

Aegis-Grid strictly adheres to **Hexagonal Architecture** with distinct ports and adapters for four main DDD Bounded Contexts:
1. Geospatial
2. Agent
3. Threat
4. C2

The application utilizes **CQRS** (Command Query Responsibility Segregation) and an **Event-Driven Architecture** (Event Bus) for inter-service communication. Robustness is ensured via the **Circuit Breaker** and **Saga Patterns**.

```mermaid
graph TD;
    A[Drone/Radar Feeds] -->|WebSockets| B(FastAPI Ingestion);
    B -->|AsyncPG| C[(PostGIS)];
    C --> D{LangGraph Supervisor};
    D -->|Query| E[(Qdrant Vector DB)];
    D -->|Task| F[Intel Analyst Agent];
    D -->|Task| G[Tactical Planner Agent];
    F --> H[C2 Dashboard];
    G --> H;
```

## Setup & Deployment (Docker Compose)
The easiest way to spin up the entire Aegis-Grid stack (Backend, Frontend, PostGIS, Qdrant, Prometheus, Grafana) is via Docker Compose.

### Prerequisites
*   Docker & Docker Compose installed
*   An LLM provider API key (OpenAI for testing, or Ollama/LocalAI URL for true air-gapped deployment).

### Environment Variables
| Variable | Description | Default |
| -------- | ----------- | ------- |
| `ENVIRONMENT` | Deployment environment | `development` |
| `JWT_SECRET` | Secret key for JWT | `supersecretdefensekey_change_in_prod` |
| `DATABASE_URL` | PostGIS connection URL | `postgresql+asyncpg://aegis_admin:secure_password@postgis:5432/aegis_spatial` |
| `QDRANT_URL` | Qdrant vector DB URL | `http://qdrant:6333` |
| `OLLAMA_URL` | Local LLM URL | `http://ollama:11434` |
| `OPENAI_API_KEY` | OpenAI API Key (if used) | |
| `MAX_WS_CONNECTIONS` | Max WebSocket connections | `1000` |
| `GPS_JAMMED_NOISE_SIGMA`| GPS noise sigma | `50.0` |

### Steps
1. Clone the repository
2. Create a `.env` file in the root directory and populate it.
3. Build and launch the stack:
   `docker-compose up --build -d`
4. Access the C2 Dashboard: `http://localhost:5173`
5. Access the API Documentation: `http://localhost:8000/docs`

## Local Development (Without Docker)
### Backend
`cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000`

### Frontend
`cd frontend && npm install && npm run dev`

## Testing
Run the Pytest suite for the backend:
`cd backend && PYTHONPATH=. pytest tests/ -v --cov=main`

## Security
* mTLS between containers
* JWT authentication with HttpOnly cookies
* RBAC (Role-Based Access Control)
* ABAC (Attribute-Based Access Control) for document classification
* Pydantic v2 strict mode
* Content-Security-Policy headers
* 10MB input size limit
* Immutable audit logging

## Disclaimer
This project is a conceptual software architecture demonstration. It is not classified, nor is it intended for actual kinetic military operations without extensive hardware integration, ruggedization, and rigorous Authority to Operate (ATO) compliance testing.
