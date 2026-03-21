<p align="center">
  <img src="https://raw.githubusercontent.com/TarikSert/Aerial-Multi-Agent-Simulation-Engine/main/assets/logo.png" width="100" />
</p>

<h1 align="center">🛡️ Aegis-Grid Tactical Intelligence & C2 Engine</h1>

<p align="center">
  <strong>A High-Fidelity Tactical Command & Control (C2) Dashboard & Multi-Agent Evaluation Environment</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/React-Vite-red?style=for-the-badge&logo=react" alt="React" />
  <img src="https://img.shields.io/badge/Deck.gl-Visualizer-yellow?style=for-the-badge" alt="Visualizer" />
  <img src="https://img.shields.io/badge/Status-Active%20Research-orange?style=for-the-badge" alt="Status" />
</p>

---

## 📖 TABLE OF CONTENTS
- [1. Executive Summary](#1-executive-summary)
- [2. Major Architecture (Major-to-Major)](#2-major-architecture)
- [3. Technical Specifications (Minor-to-Minor)](#3-technical-specifications)
- [4. Multi-Agent BDI Logic](#4-multi-agent-bdi-logic)
- [5. Geospatial Mathematics](#5-geospatial-mathematics)
- [6. Live Simulator Workflows](#6-live-simulator-workflows)
- [7. Installation & Deployment](#7-installation--deployment)
- [8. GitHub Actions & CI/CD](#8-github-actions--cicd)

---

## 1. EXECUTIVE SUMMARY
**Aegis-Grid** represents the cutting edge of modern tactical systems. It is an air-gapped capable, multi-agent response system that fuses real-time geospatial telemetry with operational doctrines. 

Key Mission Objectives:
- **Autonomous Coordination**: Real-time tracking of drone swarms and hostile incursions.
- **Contested Environments**: Built-in Electronic Warfare (EW) simulation for GPS-denied navigation study.
- **HITL Integration**: Seamless Human-in-the-Loop approval chains for ethical AI engagement.

---

## 2. MAJOR ARCHITECTURE
### 🏆 System Blueprint
Built on a **Hexagonal Design (Domain Driven Design)** to ensure the core business logic is decouple from transient frameworks (FastAPI/React).

- **Domain Layer**: Pure tactical logic, unit models, and state machines.
- **Infrastructure Layer**: WebSocket adapters, SQLite persistence, and Qdrant vector retrieval.
- **Application Layer**: C2 Dashboard (React/Vite) providing the global common operating picture (COP).

---

## 3. TECHNICAL SPECIFICATIONS
### 🧩 Backend (Python 3.10+)
- **FastAPI**: Asynchronous event handling with high-throughput WebSocket streaming.
- **Uvicorn**: Lightning-fast ASGI server for production-grade stability.
- **Scenario Simulator**: Physics-aware 1Hz update loop with automated hostile incursion logic.

### 🖼️ Frontend (React 18 + Vite)
- **Deck.gl**: WebGL2-powered geospatial rendering for smooth 60FPS unit tracking.
- **Zustand**: High-performance, flux-pattern state management.
- **Lucide Icons**: Military-grade, vectorized iconography.

---

## 4. MULTI-AGENT BDI LOGIC
The system utilizes a **Belief-Desire-Intention (BDI)** model for its autonomous agents:
1.  **Beliefs**: Fused geospatial telemetry (Positions, Threat Scores).
2.  **Desires**: Strategic objectives (e.g., Maintain exclusion zones).
3.  **Intentions**: Tactical plans (e.g., Intercept Hostile ID: 48F2).

| Agent Role | Responsibility | Logic Pattern |
| :--- | :--- | :--- |
| **Supervisor** | Event Routing & State Initializer | LangGraph Controller |
| **Intel Analyst** | Doctrine RAG & ROE Extraction | ReAct & HyDE |
| **Tactical Planner**| Interception & Routing | Tree of Thoughts (ToT) |

---

## 5. GEOSPATIAL MATHEMATICS
The engine performs complex calculations to ensure tactical accuracy:
- **Haversine Distance**: High-velocity intercept point calculations.
- **Theta***: Any-angle pathfinding for swarm avoidance of geofenced terrain.
- **Kalman Smoothing**: Dynamic jitter reduction for noisy sensors during GPS Jamming.

---

## 6. LIVE SIMULATOR WORKFLOWS

### ⚡ WORKFLOW A: TACTICAL ENGAGEMENT
1.  **Monitor**: View the live feed at (120.5E, 24.5N) - the Taiwan Strait theater.
2.  **Alert**: Supervisor AI triggers an alert when a hostile unit breaches the 5km exclusion zone.
3.  **Decision**: 
    - **EXECUTE**: Neutralizes the threat and purges hostile entities from the map.
    - **ABORT**: Halt all current engagements and stand down assets.

---

## 7. INSTALLATION & DEPLOYMENT
### 🛠️ Local Environment Setup
```bash
# Clone the repository
git clone https://github.com/imshivanshutiwari/Aegis-Grid.git

# Terminal 1: Backend
cd aegis-grid/backend
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
python -m uvicorn main.main:app --port 8000

# Terminal 2: Frontend
cd aegis-grid/frontend
npm install
npm run dev
```

---

## 8. GITHUB ACTIONS & CI/CD
The project includes automated pipelines in `.github/workflows/`:
- **CI Build**: Validates frontend builds on every push.
- **Test Suite**: Automated Python unit testing for simulator consistency.
- **Security Scans**: Scrutinizes dependencies for tactical-grade reliability.

---
<p align="center">
  Built under the <strong>IRON PROTOCOL</strong>. 🛡️
</p>
