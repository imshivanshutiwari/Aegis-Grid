<div align="center">
  <img src="https://img.icons8.com/isometric/512/rocket.png" width="120" />
</div>

<h1 align="center">⚔️ AEGIS-GRID: TACTICAL INTELLIGENCE ENGINE ⚔️</h1>

<p align="center">
  <strong>A High-Fidelity Beyond Visual Range (BVR) Combat & Tactical AI Evaluation Environment</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/FastAPI-Framework-red?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Deck.gl-Mapbox-yellow?style=for-the-badge" alt="Visualizer" />
  <img src="https://img.shields.io/badge/Status-Active%20Research-orange?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Protocol-IRON%20SIGMA-blueviolet?style=for-the-badge" alt="Protocol" />
</p>

---

## 📑 TABLE OF CONTENTS
1.  [Executive Summary](#-executive-summary)
2.  [Mission-Critical Objectives](#-mission-critical-objectives)
3.  [Major Architecture (Major-to-Major)](#-major-architecture)
4.  [Technical Specifications (Minor-to-Minor)](#-technical-specifications)
5.  [Multi-Agent Intelligence System (BDI)](#-multi-agent-intelligence-system)
6.  [Geospatial Mathematics & Tactical Logic](#-geospatial-mathematics--tactical-logic)
7.  [Electronic Warfare & Signal Degradation](#-electronic-warfare--signal-degradation)
8.  [Interactive Workflows (Comprehensive)](#-interactive-workflows-comprehensive)
9.  [File-by-File Technical Manifest](#-file-by-file-technical-manifest)
10. [Installation & Deployment Roadmap](#-installation--deployment-roadmap)
11. [Strategic Roadmap](#-strategic-roadmap)
12. [Legal Disclaimer](#-legal-disclaimer)

---

## 🚀 I. EXECUTIVE SUMMARY
**AEGIS-GRID** is a cutting-edge, air-gapped capable Command and Control (C2) system designed for the modern contested battlespace. It represents a paradigm shift in tactical awareness, fusing real-time geospatial telemetry with deterministic, stateful Multi-Agent AI. 

Unlike traditional monitoring tools, Aegis-Grid doesn't just display data; it **reasons** over it. By ingesting Rules of Engagement (ROE) and Field Manuals into a local Retrieval-Augmented Generation (RAG) pipeline, the system provides Human-in-the-Loop (HITL) commanders with explainable, doctrine-aligned response proposals.

---

## 🎯 II. MISSION-CRITICAL OBJECTIVES
-   **Autonomous Threat Evaluation**: Real-time analysis of unit movement patterns to distinguish between routine patrols and hostile incursions.
-   **Resilient Coordination**: Maintaining a Common Operating Picture (COP) under high-latency and contested Electronic Warfare (EW) conditions.
-   **Ethical AI Engagement**: Ensuring every kinetic proposal is backed by a transparent chain of reasoning and doctrine citation.
-   **Zero-Trust Edge Deployment**: Optimized for deployment on ruggedized edge hardware without external cloud dependencies.

---

## 🏗️ III. MAJOR ARCHITECTURE
### 🏆 The Hexagonal Core
The system is built on **Hexagonal Architecture (Ports and Adapters)** to isolate the core tactical logic from external complexities.

#### 1. The Domain Layer (Tactical Core)
-   **Unit Entities**: Self-contained state machines for every friendly, hostile, and unknown asset.
-   **Tactical Rules**: In-memory logic for Geofencing, Proximity Alerts, and Velocity Vector calculation.

#### 2. The Infrastructure Layer (The Adapters)
-   **WebSocket Adapter**: Streams 1Hz telemetry to the frontend via high-throughput async loops.
-   **Qdrant Vector Adapter**: Interacts with the local vector store for millisecond RAG retrieval.
-   **Deck.gl Visualizer**: Translates raw JSON telemetry into GPU-accelerated tactical maps.

---

## ⚙️ IV. TECHNICAL SPECIFICATIONS
### 🧩 Backend: The Python Engine
-   **FastAPI Utility**: Handles the lifecycle of the C2 server, providing both RESTful endpoints for configuration and WebSockets for live streams.
-   **Asyncio Task Management**: Uses a centralized event loop to handle hundreds of concurrent unit updates without blocking the thread.
-   **Uvicorn Worker**: Optimized ASGI worker for handling high-frequency tactical data.

### 🖼️ Frontend: The C2 Interface
-   **React 18**: Component-based UI for the Sidebar, Logs, and Alert Panels.
-   **Deck.gl Visualization**: Uses WebGL2 to render thousands of points on a Mapbox base layer with zero lag.
-   **Zustand State Store**: A lightweight, high-performance state manager that ensures the UI is always synced with the latest backend telemetry.

---

## 🧠 V. MULTI-AGENT INTELLIGENCE SYSTEM
Aegis-Grid utilizes a **Belief-Desire-Intention (BDI)** model, orchestrated via **LangGraph**.

### 🎭 Agent Roles
-   **Intel Analyst Agent**:
    -   *Input*: Raw threat alerts.
    -   *Action*: Queries the Qdrant Vector DB for specific Rules of Engagement (ROE).
    -   *Output*: Doctrine-aligned threat summary.
-   **Tactical Planner Agent**:
    -   *Input*: Intel summary + Geospatial telemetry.
    -   *Action*: Calculates intercept or evasion routes.
    -   *Output*: Proposed response plan (Execute/Abort).
-   **Supervisor Agent**:
    -   *Action*: Coordinates the flow between Intel and Planning, ensuring the HITL commander only sees finalized, verified data.

---

## 📏 VI. GEOSPATIAL MATHEMATICS & TACTICAL LOGIC
The engine utilizes high-precision spherical geometry to ensure tactical accuracy:

1.  **Haversine Distance**: Used for relative distance calculation between moving assets.
    -   *Formula*: $d = 2r \arcsin(\sqrt{\sin^2(\frac{\Delta\phi}{2}) + \cos\phi_1\cos\phi_2\sin^2(\frac{\Delta\lambda}{2})})$
2.  **Bearing Calculation**: Determines the intercept heading for automated assets.
3.  **Geofential Breach Detection**: A 5.0km exclusion zone around (120.5E, 24.5N) is monitored at 1Hz.

---

## 📡 VII. ELECTRONIC WARFARE & SIGNAL DEGRADATION
Aegis-Grid simulates modern Electronic Warfare (EW) through a dynamic **GPS Jamming** toggle.

-   **Logic**: When active, a Gaussian noise filter is applied to all incoming telemetry.
-   **Visual Feedback**: The frontend introduces a "Jitter" effect and expands the "Uncertainty Layer" (Semi-transparent circle around assets).
-   **Agent Response**: AI agents switch from "Precise Tracking" to "Probabilistic Search" mode, increasing the search radius for hostile assets.

---

## 🛠️ VIII. INTERACTIVE WORKFLOWS (COMPREHENSIVE)

### 🔴 WORKFLOW 1: LOCAL DEVELOPMENT SETUP
1.  **Repository Initialization**: `git clone https://github.com/imshivanshutiwari/Aegis-Grid.git`
2.  **Environment Sync**: Copy `.env.example` to `.env` and fill in tactical keys.
3.  **Backend Ignition**: 
    - `cd aegis-grid/backend`
    - `pip install -r requirements.txt`
    - `python -m uvicorn main.main:app --port 8000`
4.  **Frontend Ignition**:
    - `cd aegis-grid/frontend`
    - `npm install`
    - `npm run dev`

### 🔵 WORKFLOW 2: TACTICAL THREAT RESPONSE (HITL)
1.  **Detection**: A red hostile dot appears on the Taiwan Strait map.
2.  **Alert Generation**: The `CRITICAL THREATS` panel flashes red with ID and type.
3.  **Agent Reasoning**: The `AGENT REASONING LOGS` scroll with step-by-step logic (e.g., "Scanning ROE Database...").
4.  **HITL Intervention**:
    - Click **EXECUTE**: The backend clears the threat and broadcasts a "Neutralized" event.
    - Click **ABORT**: The threat remains, but the tactical plan is archived.

### 🟡 WORKFLOW 3: GPS JAMMING SIMULATION
1.  **Activation**: Toggle the **GPS JAMMING** switch in the sidebar.
2.  **Visual Verification**: Observe the unit markers jittering and the blue uncertainty layers expanding.
3.  **Tactical Analysis**: Note how the distance calculations become +/- 500m varied due to simulated sensor noise.

---

## 📂 IX. FILE-BY-FILE TECHNICAL MANIFEST

### 🛡️ Core Root
-   `README.md`: The central command manual.
-   `.gitignore`: Prevents build artifacts (node_modules, pycache) from bloating the repo.
-   `.github/workflows/ci.yml`: Automated CI/CD pipeline for build validation.

### 🐍 Backend (`/aegis-grid/backend`)
-   `main/main.py`: FastAPI entry point and WebSocket bridge.
-   `main/simulator.py`: **The Heart**. Contains the 1Hz update loop and Taiwan Strait coordinate logic.
-   `models/`: Pydantic schemes for tactical data.
-   `services/`: Business logic for RAG and Agentic flows.

### ⚛️ Frontend (`/aegis-grid/frontend`)
-   `src/App.jsx`: Main dashboard layout with Grid system for the sidebar.
-   `src/components/TacticalMap.jsx`: Deck.gl logic including GPS Jitter rendering.
-   `src/index.css`: Custom scrollbars and theme styling.

---

## 🚢 X. INSTALLATION & DEPLOYMENT ROADMAP
### 📦 Docker Deployment (Alpha)
The system is being containerized for seamless deployment across edge nodes.
```bash
# Planned deployment pattern
docker-compose up --build -d
```

### 🔐 Air-Gapped Strategy
To run AEGIS-GRID in a truly disconnected environment:
1.  Pre-download the **Llama-3** or **Gemma** weights.
2.  Initialize the **Qdrant** volume with tactical docs.
3.  Point the `OLLAMA_URL` in `.env` to the local hosting container.

---

## 🗺️ XI. STRATEGIC ROADMAP
- [x] **V1.0**: Live Geospatial Telemetry & HITL Interaction.
- [x] **V1.1**: GPS Jamming Simulation & Visual Feedback.
- [ ] **V1.2**: Swarm Coordination Logic (Friendly Drone Intercepts).
- [ ] **V1.3**: Advanced Thermal & Infrared Layer Toggles.
- [ ] **V1.4**: Full 3D Terrain Integration with Cesium.

---

## ⚖️ XII. LEGAL DISCLAIMER
This project is a **conceptual software architecture demonstration**. It is NOT intended for actual kinetic operations. The developers are not responsible for any misuse. Built under the **IRON PROTOCOL** for civilian and educational research into tactical-grade AI architectures.

---
<p align="center">
  Generated by the <strong>Antigravity Intelligence Sub-Agent</strong>. 🦅
</p>
