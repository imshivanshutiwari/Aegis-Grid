# 🛡️ KAVACH-SIGMA

**Kinetic Autonomous Vectorized Analysis & Countermeasure Hub — SIGINT Intelligence & Multi-Agent**

An autonomous, multi-agent SIGINT PED framework that transforms raw RF spectrum data into real-time tactical countermeasures using Agentic Reasoning and Geospatial RAG.

## Problem Addressed

Modern battlefields are saturated with RF noise. Current manual SIGINT analysis takes hours to identify a "Signal of Interest". KAVACH-SIGMA aims to reduce this by automatically classifying signals using Deep Learning, evaluating intent with LangGraph Agentic Reasoners, and querying a vector DB for known countermeasures.

## Technology Stack

* **Orchestration**: LangGraph (Agentic loops)
* **Perception**: PyTorch (RF Modulation Detection)
* **Memory**: Qdrant (Vector DB for Electronic Order of Battle - EOB)
* **Streaming**: FastAPI + WebSockets (Real-Time Sensor Ingestion)
* **Deployment**: Docker Compose

## Core Modules

* `agents/`: Core cognitive components coordinating Analyst, Tactical, and ELINT logic.
* `core/`: PyTorch models and DSP functions handling signal perception.
* `memory/`: Ingestion and retrieval systems from the Qdrant EOB database.
* `api/`: FastAPI entrypoints for websocket streaming and HTTP triggers.

## Quick Start (Deployment "War-Manual")

Deploy KAVACH-SIGMA instantly via Docker Compose:

```bash
cd kavach-sigma
docker-compose up --build -d
```

This starts the main intelligence API and the embedded Qdrant server for the memory store.
You can access the API docs at `http://localhost:8000/docs`.

### Testing
Run tests to ensure functionality:

```bash
cd kavach-sigma
PYTHONPATH=. pytest tests/ --cov=.
```

## Disclaimer
This project is for simulation and demonstration purposes, demonstrating Agentic AI within Electronic Warfare architecture.