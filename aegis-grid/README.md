# 🦅 Aegis-Grid: Tactical Multi-Agent C2 Intelligence System

**Aegis-Grid** is a state-of-the-art Command and Control (C2) Dashboard and Tactical Simulator. It is designed to demonstrate multi-agent coordination, real-time geospatial intelligence, and Human-in-the-Loop (HITL) decision-making in contested environments.

---

## 🏗️ SYSTEM ARCHITECTURE Overview

### 🎖️ High-Level Mission
The system operates as a **Tactical Supervisor**, bridging the gap between autonomous AI agents and human commanders. It fuses live telemetry from friendly units and hostile threats into a single "God-eye" view.

### 🧩 Core Components (Major-to-Major)
1.  **C2 Tactical Dashboard (Frontend)**: A high-performance React application utilizing `Deck.gl` for hardware-accelerated geospatial rendering.
2.  **Tactical Simulator (Backend)**: A high-fidelity Python-based engine that simulates unit dynamics, threat incursions, and signal interference.
3.  **Agent Reasoning Engine**: A mock-agent logic that provides situational awareness logs and tactical recommendations.

---

## 📡 TECHNICAL DEEP DIVE (Minor-to-Minor)

### 💻 Frontend Stack
- **Framework**: [React](https://reactjs.org/) + [Vite](https://vitejs.dev/) for ultra-fast HMR.
- **Geospatial Engine**: [Deck.gl](https://deck.gl/) for rendering 1000+ units with 60fps performance.
- **State Management**: [Zustand](https://github.com/pmndrs/zustand) for lightweight, high-speed tactical state updates.
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) with a custom "Tactical Dark" theme.
- **Icons**: [Lucide-React](https://lucide.dev/) for crisp, military-grade iconography.

### ⚙️ Backend Stack
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) for high-concurrency WebSocket management.
- **Simulation Environment**: `Asyncio` driven loops running at 1Hz (Tactical Update Rate).
- **Communication**: Bi-directional WebSockets using JSON-framed messaging.
- **Data Channels**:
    - `units.positions`: Real-time telemetry for all map entities.
    - `threats.alerts`: Critical notifications for hostile incursions.
    - `agents.reasoning`: NLP-formatted logs explaining the AI's internal BDI (Belief-Desire-Intention) state.

---

## 🎮 INTERACTIVE WORKFLOWS

### 🛠️ Workflow 1: Local Development Setup
1.  **Clone & Enter**:
    ```bash
    git clone https://github.com/imshivanshutiwari/Aegis-Grid.git
    cd Aegis-Grid
    ```
2.  **Start Backend**:
    ```bash
    cd aegis-grid/backend
    $env:PYTHONPATH="."
    python -m uvicorn main.main:app --port 8000 --reload
    ```
3.  **Start Frontend**:
    ```bash
    cd aegis-grid/frontend
    npm install
    npm run dev -- --port 3000
    ```

### 🗺️ Workflow 2: Tactical Monitoring
- **Navigate**: Use the map to zoom into the **Taiwan Strait**, our primary Area of Responsibility (AOR).
- **Identify**: 
    - 🔵 **Blue**: Friendly assets (Drones/Ground Units).
    - 🔴 **Red**: Hostile incursions moving towards the center.
    - 🟡 **Yellow Glow**: Critical threats identified by the Supervisor AI.

### ⚡ Workflow 3: HITL Response (Execute/Abort)
1.  **Detect**: Supervisor AI identifies a critical threat and logs it in the **Agent Reasoning Panel**.
2.  **Analyze**: Review the threat description in the **Critical Threats** list.
3.  **Decision**:
    - Click **EXECUTE**: Authorized tactical response. The system will neutralize (remove) the hostile units from the map.
    - Click **ABORT**: Halt engagement. System stands down and logs the commander's override.

### 📡 Workflow 4: Electronic Warfare (EW) Simulation
1.  **Trigger**: Click the **Jam GPS** button in the top header.
2.  **Observe**:
    - Map units will begin to **Jitter**, simulating signal interference.
    - Orange **Uncertainty Radii** will appear around units, showing the loss of precise PNT (Position, Navigation, and Timing).
3.  **Recover**: Click **Jam GPS** again to restore signal integrity and clear the "GPS JAMMED" status.

---

## 📁 REPOSITORY STRUCTURE
```text
Aegis-Grid/
├── aegis-grid/
│   ├── backend/
│   │   ├── main/
│   │   │   ├── main.py        # FastAPI Entry Point & WS Handler
│   │   │   ├── simulator.py   # Tactical Incursion Engine
│   │   │   └── adapters/      # Interface Adapters (Websocket Manager)
│   │   └── tests/             # Unit and Integration Tests
│   └── frontend/
│       ├── src/
│       │   ├── App.jsx        # Main C2 UI Logic
│       │   ├── store.js       # Global Tactical Store (Zustand)
│       │   └── components/    # TacticalMap.jsx (Deck.gl integration)
│       └── package.json       # Frontend Dependencies
└── docs/                      # Architectural Deep Dives
```

---

## 🛡️ MISSION STANDARDS
This project is built to the **IRON PROTOCOL** standard:
- **Resilience**: Automatic reconnection on WebSocket failure.
- **Responsiveness**: <50ms UI latency for tactical updates.
- **Relevance**: Simulation coordinates set to real-world strategic theaters (Taiwan Strait).

**Built with passion for next-gen Defense Technology.** 🦅
