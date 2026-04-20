# 🌊 AI Baja Agent

> A production-grade **AI Baja Agentic** for travel planning along the Baja California, México  — powered by LangGraph, FastAPI, and a multi-node ReAct architecture with real-time observability.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.129-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-purple)](https://langchain-ai.github.io/langgraph/)
[![React](https://img.shields.io/badge/React-Vite-61DAFB?logo=react&logoColor=black)](https://vitejs.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is this?

AI Baja Agent is a **multi-agent travel planning system** that takes a natural language request like _"Plan a 3-day Baja beach trip"_ and returns a structured, actionable plan — complete with a live map route, day-by-day itinerary, local food recommendations, and a full budget breakdown.

Under the hood, a LangGraph `StateGraph` orchestrates thirteen specialized nodes across intent classification, planning, enrichment, validation, memory, and self-critique — all tracked in real time via Langfuse.

This is not a wrapper around a single LLM call. It is a production-style agentic system with a typed shared state, conditional routing, multi-provider LLM support, and full observability.

---

## Demo

> _Add a screenshot or GIF here after running the app locally._

```
User: "Plan a 3-day Baja road trip with seafood and beaches"

intent_classifier → trip_planner_router → [travel_node, food_node,
budget_node, map_enrichment_node] → travel_validator → critic →
confidence → summary → final_compiler → Response
```

**Sample output:**
- 🚗 **Route:** Tijuana → Rosarito → Puerto Nuevo → Ensenada (~120 km, real ORS driving route)
- 📅 **Itinerary:** 3 days structured by morning / afternoon / evening
- 🍽️ **Food:** Baja Med cuisine, Puerto Nuevo lobster, street tacos
- 💰 **Budget:** Accommodation + food + transport + activities, fully itemized
- 🗺️ **Map:** Interactive Leaflet map with polyline and stop markers

---

## Architecture

```
Client (React UI + Leaflet map)
        │
        ▼
FastAPI  /chat  endpoint  (app/routes.py)
        │
        ▼
Agent Runtime — LangGraph StateGraph  (agent/orchestrator.py)
        │
        ├── intent_classifier         → classifies request type
        ├── preference_extractor      → pulls user preferences from message
        ├── history_node              → loads prior session context
        ├── trip_planner_router_node  → conditional routing to tool nodes
        │       │
        │       ├── travel_node           → day-by-day itinerary
        │       ├── food_node             → local cuisine recommendations
        │       ├── budget_node           → cost breakdown
        │       └── map_enrichment_node   → ORS real driving route + coords
        │               └── map_tool      → OpenRouteService API wrapper
        │
        ├── travel_validator_node     → validates itinerary completeness
        ├── memory_manager            → writes session state
        ├── critic_node               → scores plan quality (1–10)
        ├── confidence_node           → computes output confidence score
        ├── summary_node              → generates natural language summary
        └── final_compiler_node       → assembles structured JSON response
                │
                ▼
        Client Response
```

### Shared state

All nodes read from and write to a single typed `BajaState` object (`state/bajastate.py`), passed through the graph at each step. This makes the agent loop fully inspectable — every node's contribution is visible in the state diff.

### Key design decisions

| Decision | Rationale |
|---|---|
| LangGraph `StateGraph` | Explicit state transitions, conditional edges, easy to debug |
| `BajaState` typed state object | Single source of truth across all 13 nodes |
| `intent_classifier` as entry point | Prevents wasted node calls on unsupported request types |
| `trip_planner_router_node` with conditional routing | Only invokes relevant tool nodes per request |
| `travel_validator_node` before critic | Catches structural errors before quality scoring |
| `critic_node` + `confidence_node` in loop | Self-correction and calibrated confidence before response |
| ORS for real routing | Actual driving distances and durations, not straight-line estimates |
| Groq (llama-3.1-8b-instant) as default | Fast inference, low latency for agentic loops |

---

## Node reference

| Node | File | Responsibility |
|---|---|---|
| `intent_classifier` | `nodes/intent_classifier.py` | Classifies request as trip / food / budget / general |
| `preference_extractor` | `nodes/preference_extractor.py` | Extracts duration, style, budget tier from message |
| `history_node` | `nodes/history_node.py` | Loads prior turns from session memory |
| `trip_planner_router_node` | `nodes/trip_planner_router_node.py` | Conditional edge routing to tool nodes |
| `travel_node` | `nodes/travel_node.py` | Builds day-by-day itinerary with Tavily enrichment |
| `food_node` | `nodes/food_node.py` | Local cuisine recommendations per day |
| `budget_node` | `nodes/budget_node.py` | Itemized cost estimate |
| `map_enrichment_node` | `nodes/map_enrichment_node.py` | Enriches stops with ORS route data |
| `map_tool` | `nodes/map_tool.py` | OpenRouteService API wrapper |
| `travel_validator_node` | `nodes/travel_validator_node.py` | Validates itinerary structure and completeness |
| `memory_manager` | `nodes/memory_manager.py` | Reads / writes session state |
| `critic_node` | `nodes/critic_node.py` | Scores plan quality, flags gaps |
| `confidence_node` | `nodes/confidence_node.py` | Computes output confidence score |
| `summary_node` | `nodes/summary_node.py` | Generates natural language trip summary |
| `final_compiler_node` | `nodes/final_compiler_node.py` | Assembles final structured JSON response |

---

## Tech stack

### Backend
| Layer | Technology |
|---|---|
| API server | FastAPI + Uvicorn |
| Agent framework | LangGraph + LangChain |
| LLM — primary | Groq (`llama-3.1-8b-instant`) |
| LLM — fallback | Google Gemini |
| Web search | Tavily |
| Map routing | OpenRouteService (ORS) |
| Observability | Langfuse (US cloud) |
| Data validation | Pydantic v2 |
| Config management | `app/config.py` |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 18 + Vite |
| Map | react-leaflet + OpenStreetMap tiles |
| Styling | Inline styles (zero build dependency) |

---

## Project structure

```
ai-baja-agent/
├── agent/
│   └── orchestrator.py          # LangGraph StateGraph definition
├── app/
│   ├── agent.py                 # Agent entry point / runner
│   └── routes.py                # FastAPI route handlers
├── database/
│   └── database.py              # Session / memory persistence
├── graph/
│   └── builder.py               # Graph compilation + edge wiring
├── llm/
│   └── provider.py              # Multi-provider LLM factory (Groq / Google)
├── nodes/
│   ├── intent_classifier.py
│   ├── preference_extractor.py
│   ├── history_node.py
│   ├── trip_planner_router_node.py
│   ├── travel_node.py
│   ├── food_node.py
│   ├── budget_node.py
│   ├── map_enrichment_node.py
│   ├── map_tool.py
│   ├── travel_validator_node.py
│   ├── memory_manager.py
│   ├── critic_node.py
│   ├── confidence_node.py
│   ├── summary_node.py
│   └── final_compiler_node.py
├── routing/
│   └── routes.py                # Conditional edge logic for the graph
├── state/
│   └── bajastate.py             # Typed BajaState shared across all nodes
├── frontend/
│   ├── src/
│   │   └── App.jsx              # Map + plan UI
│   ├── index.html
│   └── package.json
├── docs/
│   └── screenshots/             # UI and Langfuse screenshots
├── .env.example
├── .gitignore
├── main.py                      # Main
├── requirements.txt
└── README.md
```

---

## Getting started

### Prerequisites

- Python 3.11
- Node.js 18+
- A Groq API key (free tier is sufficient)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ai-baja-agent.git
cd ai-baja-agent
```

### 2. Set up the backend

```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copy and fill in the environment file:

```bash
cp .env.example .env
```

Start the API server:

```bash
uvicorn app.agent:app --reload --port 8000
```

### 3. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes (if using Groq) | Groq inference API key |
| `GROQ_MODEL` | Yes | Model name, e.g. `llama-3.1-8b-instant` |
| `GOOGLE_API_KEY` | Yes (if using Google) | Google Gemini API key |
| `LLM_PROVIDER` | Yes | `"groq"` or `"google"` |
| `TAVILY_API_KEY` | Yes | Tavily search key for travel/food enrichment |
| `ORS_API_KEY` | Yes | OpenRouteService key for real driving routes |
| `LANGFUSE_PUBLIC_KEY` | Optional | Langfuse project public key |
| `LANGFUSE_SECRET_KEY` | Optional | Langfuse project secret key |
| `LANGFUSE_BASE_URL` | Optional | `https://us.cloud.langfuse.com` |

See `.env.example` for the full template.

---

## API reference

### `POST /chat`

**Request**
```json
{
  "session_id": "demo",
  "message": "Plan a 3-day Baja beach trip"
}
```

**Response**
```json
{
  "response": {
    "route": {
      "segments": [
        { "from": "Tijuana", "to": "Rosarito", "distance_human": "32 km" }
      ],
      "summary": {
        "total_distance_human": "120 km",
        "total_duration_human": "2h 10min",
        "travel_style": "Coastal road trip"
      }
    },
    "travel": {
      "Day 1": [
        { "time": "09:00", "activity": "Depart Tijuana, drive to Rosarito" }
      ]
    },
    "food": {
      "Day 1": [
        { "meal": "Lunch", "description": "Fish tacos at La Guerrerense, Ensenada" }
      ]
    },
    "budget": {
      "accommodation": 180,
      "food": 90,
      "transportation": 45,
      "activities": 30,
      "total": 345
    }
  }
}
```

---

## Observability

Every agent run is traced end-to-end in **Langfuse**:

- Full node-by-node trace with latency per step
- Token counts and LLM call details per node
- Critic score and confidence score per run
- Session history across multi-turn conversations

Traces are visible at [us.cloud.langfuse.com](https://us.cloud.langfuse.com) under your project dashboard.

> Add a Langfuse screenshot here to show recruiters what the trace looks like.

---

## Roadmap

- [ ] Streaming responses via WebSocket (real-time token output)
- [ ] PostgreSQL persistence for long-term session memory
- [ ] Expanded location graph beyond the Baja corridor
- [ ] Voice input via Web Speech API
- [ ] Docker Compose for one-command local setup

---

## Contributing

Pull requests are welcome. For major changes, open an issue first.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'add: my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

[MIT](LICENSE)

---

## Author

**Eduardo Herrera** — Building production-grade AI systems from Tijuana, Baja California.

> Built as part of a larger **AI Baja Agent** portfolio — demonstrating LangGraph, FastAPI, multi-node tool orchestration, typed shared state, and full Langfuse observability.
