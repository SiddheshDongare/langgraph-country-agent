# Country Intelligence Agent

An AI-powered agent that answers natural-language questions about any country in the world.
Built with **LangGraph**, **FastAPI**, and the [REST Countries API](https://restcountries.com),
it extracts user intent via an LLM, fetches real-time data, and synthesises a grounded answer —
all within a deterministic, three-node graph.

---

## Table of Contents

- [Overall Architecture](#overall-architecture)
- [Agent Flow](#agent-flow)
  - [Example Walkthroughs](#example-walkthroughs)
- [Production Behaviour](#production-behaviour)
- [Known Limitations & Trade-offs](#known-limitations--trade-offs)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration Reference](#configuration-reference)
- [Testing](#testing)
- [Frontend (UI)](#frontend-ui)

---

## Overall Architecture

```
┌────────────────────────────────────────────────────────┐
│                      Client                            │
│  Next.js UI  /  curl  /  any HTTP consumer             │
└──────────────────────┬─────────────────────────────────┘
                       │  POST /ask  { "question": "…" }
                       ▼
┌────────────────────────────────────────────────────────┐
│               FastAPI Server (api.py)                   │
│  • POST /ask   → runs the LangGraph agent              │
│  • GET  /health → liveness probe                       │
│  • CORS middleware (configurable origins)               │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────┐
│            LangGraph StateGraph (graph.py)              │
│                                                        │
│  START                                                 │
│    │                                                   │
│    ▼                                                   │
│  ┌──────────────────┐                                  │
│  │  identify_intent │  ← LLM (structured output)      │
│  └────────┬─────────┘                                  │
│           │                                            │
│     ┌─────┴──────┐                                     │
│     │ has error?  │                                     │
│     └─────┬──────┘                                     │
│      no   │   yes ─────────────┐                       │
│           ▼                    ▼                       │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │   invoke_tool    │  │                  │            │
│  │  (REST Countries │  │                  │            │
│  │   API via httpx) │  │                  │            │
│  └────────┬─────────┘  │                  │            │
│           │             │                  │            │
│           ▼             │                  │            │
│  ┌──────────────────┐   │                  │            │
│  │ synthesize_answer│ ◄─┘                  │            │
│  │   (LLM)         │◄─────────────────────┘            │
│  └────────┬─────────┘                                  │
│           │                                            │
│           ▼                                            │
│          END                                           │
└────────────────────────────────────────────────────────┘
```

### Key Modules

| Module | Responsibility |
|---|---|
| **`graph.py`** | Defines `AgentState` (a `TypedDict`) and wires the three nodes into a compiled `StateGraph`. Contains the conditional routing function `_route_after_intent`. |
| **`nodes.py`** | Implements the three node functions: `identify_intent`, `invoke_tool`, and `synthesize_answer`. Each reads from and writes back to the shared `AgentState`. |
| **`tools.py`** | A LangChain `@tool`-decorated async function `fetch_country_info` that calls the REST Countries API, disambiguates results, and returns structured data. |
| **`models.py`** | Pydantic models — `IntentResult` for LLM structured output and `CountryInfo` / `CurrencyInfo` for parsing & validating raw API responses. Also defines the `VALID_FIELDS` set. |
| **`settings.py`** | `pydantic-settings`-based `Settings` class. Loads all configuration from environment variables (`COUNTRY_AGENT_*` prefix) and provides a factory method `get_llm()`. |
| **`api.py`** | FastAPI application with `POST /ask` and `GET /health` endpoints, plus CORS middleware. |
| **`main.py`** | CLI entry point — reads a question from CLI args or stdin, invokes the graph, and prints the answer. Also configures `structlog`. |

### Shared State (`AgentState`)

Every node reads from and writes to a single `TypedDict`:

```python
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]  # conversation history
    country_name: str | None       # extracted by identify_intent
    requested_fields: list[str]    # e.g. ["population", "capital"]
    api_response: list[dict] | None  # raw REST Countries data
    error: str | None              # set at any step to trigger error path
```

The `messages` key uses LangGraph's `add_messages` reducer — new messages are appended, not overwritten.

---

## Agent Flow

The agent follows a strict **three-step pipeline**:

### 1. `identify_intent` (LLM call)

- **Input:** the user's natural-language question (taken from the last `HumanMessage` in state).
- **Mechanism:** calls the configured LLM with a system prompt and receives structured output (`IntentResult`) containing `country_name` and `requested_fields`.
- **Validation:** extracted fields are checked against `VALID_FIELDS`; unrecognised fields are dropped, defaulting to `["general"]`.
- **On failure:** sets `state["error"]` and the conditional edge skips straight to `synthesize_answer`.

### 2. `invoke_tool` (API call)

- **Input:** `state["country_name"]`.
- **Mechanism:** calls `fetch_country_info`, which makes an async `httpx` GET request to `https://restcountries.com/v3.1/name/{country_name}`.
- **Disambiguation:** if the API returns multiple matches (e.g. "Georgia" matches both the country and the US state), `_disambiguate()` prefers an exact `name.common` match.
- **Error handling:** network timeouts, 404s, and HTTP errors are all caught and surfaced as a user-friendly `error` string.

### 3. `synthesize_answer` (LLM call)

- **Happy path:** the raw API data is validated through `CountryInfo.from_api_response()`, serialised to JSON, and injected into a synthesis prompt. The LLM generates a grounded, factual answer using **only** the provided data.
- **Error path:** if `state["error"]` is set (from either of the previous nodes), a different error-specific system prompt is used so the LLM can explain what went wrong and suggest alternatives.

### Conditional Routing

After `identify_intent`, the function `_route_after_intent` checks for errors:

```python
def _route_after_intent(state: AgentState) -> str:
    if state.get("error") or not state.get("country_name"):
        return "synthesize_answer"  # skip API call
    return "invoke_tool"
```

---

### Example Walkthroughs

#### ✅ Happy Path — *"What is the population of Japan?"*

```
User Question : "What is the population of Japan?"
                        │
         ┌──────────────▼──────────────┐
         │      identify_intent        │
         │  country_name = "Japan"     │
         │  requested_fields = ["population"]
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │        invoke_tool          │
         │  GET restcountries.com      │
         │       /v3.1/name/Japan      │
         │  → { population: 125836021, │
         │      capital: ["Tokyo"], …} │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │     synthesize_answer       │
         │  "Japan has a population of │
         │   125,836,021."             │
         └─────────────────────────────┘
```

#### ✅ Broad Question — *"Tell me about France"*

- `identify_intent` extracts `country_name = "France"`, `requested_fields = ["general"]`.
- `invoke_tool` fetches full country data.
- `synthesize_answer` produces a comprehensive overview (capital, population, currencies, languages, region, etc.).

#### ❌ No Country Found — *"What is the meaning of life?"*

- `identify_intent` sets `country_name = ""` → `error` is set: *"I couldn't identify a country name…"*
- **Conditional edge skips** `invoke_tool` entirely.
- `synthesize_answer` explains the error and prompts the user to ask about a specific country.

#### ❌ API Error — *"Tell me about Westeros"*

- `identify_intent` extracts `country_name = "Westeros"`.
- `invoke_tool` receives a **404** from the REST Countries API → sets `error`.
- `synthesize_answer` explains: *"No country found matching 'Westeros'…"*

---

## Production Behaviour

### Deployment Setup

| Component | Hosted On | Details |
|---|---|---|
| **Backend API** | [Render](https://render.com) | Configured via `render.yaml`. Runs `uvicorn country_agent.api:app` on `$PORT`. |
| **Frontend** | [Netlify](https://netlify.com) | Configured via `netlify.toml`. Builds from `ui/` using `npm run build`. Uses `@netlify/plugin-nextjs`. |

### Request Lifecycle (Production)

1. **User** opens the Netlify-hosted UI and types a question.
2. The Next.js client sends `POST /ask { "question": "…" }` to the Render-hosted FastAPI backend.
3. FastAPI invokes the LangGraph agent (`_run()`), which:
   - Calls the LLM (OpenAI-compatible endpoint on Groq or another provider) for intent extraction.
   - Calls the REST Countries API for factual data.
   - Calls the LLM again for answer synthesis.
4. The JSON response `{ "answer": "…" }` is returned to the UI and displayed.

### CORS

The `COUNTRY_AGENT_ALLOWED_ORIGINS` env var must include the Netlify domain (e.g. `https://your-app.netlify.app`) so the browser permits cross-origin requests from the frontend to the Render backend.

### Health Check

`GET /health` (or `HEAD /health`) returns `{"status": "ok"}`. Render can use this as an uptime check endpoint.

### Structured Logging

All backend logging uses `structlog`. In production the default `log_format` is `json`, which integrates cleanly with log aggregators (Datadog, CloudWatch, etc.). Each log entry includes a timestamp, log level, and contextual fields like `node`, `country`, and `error`.

### Settings & Secrets

All configuration is loaded from environment variables prefixed with `COUNTRY_AGENT_`:

- `COUNTRY_AGENT_OPENAI_API_KEY` — **required**, the API key for the LLM provider.
- `COUNTRY_AGENT_ALLOWED_ORIGINS` — space-separated list of allowed CORS origins.
- Other optional overrides (model name, base URL, timeout, log level).

No secrets are hardcoded; `pydantic-settings` loads them from `.env` locally or from the platform's environment configuration in production.

---

## Known Limitations & Trade-offs

### Limitations

| Limitation | Impact |
|---|---|
| **Single-turn only** | The agent does not maintain conversation history across requests. Each `/ask` call is independent — there is no session or memory. |
| **One country per query** | Intent extraction targets a single `country_name`. Questions comparing multiple countries (e.g. *"Is Brazil bigger than Argentina?"*) are not natively supported. |
| **No caching** | Identical questions re-run the full pipeline (LLM + API calls). This increases latency and token cost under repeated queries. |
| **LLM dependency for intent** | Intent extraction relies on the LLM's ability to parse free-form text. Edge cases (e.g. ambiguous names like "Georgia") depend on the LLM and then on the `_disambiguate()` heuristic. |
| **REST Countries API availability** | The agent is entirely dependent on the third-party API. If `restcountries.com` is down, all data-fetching queries fail gracefully but cannot be answered. |
| **Cold start latency** | On Render's free tier, the service spins down after inactivity. The first request after idle can take 30–60 seconds. |

### Trade-offs

| Decision | Rationale |
|---|---|
| **Deterministic graph vs. autonomous agent** | A fixed 3-node pipeline is used instead of a ReAct-style loop. This sacrifices flexibility (the agent can't decide to make multiple tool calls) but gains **predictability, debuggability, and lower token cost** — critical for a focused, single-domain agent. |
| **Structured output for intent** | Using `with_structured_output(IntentResult)` forces the LLM to return Pydantic-validated JSON. This is more reliable than parsing free-form text, but couples the system to LLMs that support structured/function-calling output. |
| **No streaming** | Responses are returned as a single JSON payload. Streaming (SSE/WebSocket) would improve perceived latency for long answers but adds complexity to both backend and frontend. |
| **Validation via Pydantic** | `CountryInfo.from_api_response()` validates and normalises the raw API data before passing it to the synthesis LLM. This adds a small overhead but ensures the prompt context is clean and well-structured, reducing hallucination risk. |
| **OpenAI-compatible interface** | The `ChatOpenAI` client with a configurable `base_url` means any OpenAI-compatible provider (Groq, Ollama, Azure, etc.) can be used. The trade-off is that provider-specific features (e.g. vision, caching) are not exposed. |

---

## Project Structure

```
langgraph-country-agent/
├── country_agent/           # Python backend package
│   ├── __init__.py
│   ├── api.py               # FastAPI app (POST /ask, GET /health)
│   ├── graph.py             # LangGraph StateGraph definition
│   ├── main.py              # CLI entry point + logging setup
│   ├── models.py            # Pydantic models (IntentResult, CountryInfo)
│   ├── nodes.py             # Node functions (identify, invoke, synthesize)
│   ├── settings.py          # Environment-based configuration
│   └── tools.py             # REST Countries API tool
├── tests/                   # pytest test suite
│   ├── conftest.py          # Shared fixtures (mocked LLM, httpx, etc.)
│   ├── test_graph.py        # Integration tests for the full graph
│   ├── test_models.py       # Unit tests for Pydantic models
│   └── test_tools.py        # Unit tests for the API tool
├── ui/                      # Next.js frontend (see Frontend section)
├── .env.example             # Template for environment variables
├── pyproject.toml           # Project metadata & dependencies
├── render.yaml              # Render deployment config
├── netlify.toml             # Netlify deployment config
└── uv.lock                  # Lockfile for uv package manager
```

---

## Getting Started

### Prerequisites

- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/) package manager
- An OpenAI-compatible API key (Groq, OpenAI, etc.)

### Setup

```bash
# Clone the repository
git clone https://github.com/SiddheshDongare/langgraph-country-agent.git
cd langgraph-country-agent

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env and set COUNTRY_AGENT_OPENAI_API_KEY
```

### Run the API Server

```bash
uv run uvicorn country_agent.api:app --reload --port 8000
```

The server starts at `http://localhost:8000`. Test it:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital of Japan?"}'
```

### Run via CLI

```bash
uv run country-agent "What languages are spoken in Switzerland?"
```

---

## Configuration Reference

All environment variables use the `COUNTRY_AGENT_` prefix:

| Variable | Default | Description |
|---|---|---|
| `COUNTRY_AGENT_OPENAI_API_KEY` | *(required)* | API key for the LLM provider |
| `COUNTRY_AGENT_LLM_MODEL` | `openai/gpt-oss-120b` | Model identifier |
| `COUNTRY_AGENT_OPENAI_BASE_URL` | `https://api.groq.com/openai/v1` | LLM API endpoint |
| `COUNTRY_AGENT_API_BASE_URL` | `https://restcountries.com/v3.1` | REST Countries API base |
| `COUNTRY_AGENT_API_TIMEOUT_SECONDS` | `10` | Timeout for external API calls |
| `COUNTRY_AGENT_ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS allowed origins |
| `COUNTRY_AGENT_LOG_LEVEL` | `INFO` | Logging level |
| `COUNTRY_AGENT_LOG_FORMAT` | `json` | `json` or `text` |

---

## Testing

Tests use `pytest` with `pytest-asyncio`, `pytest-mock`, and `respx` (for httpx mocking).

```bash
# Install dev dependencies
uv sync --extra dev

# Run all tests
uv run pytest -v
```

The test suite includes:
- **`test_models.py`** — Validates Pydantic model parsing, field defaults, and edge cases.
- **`test_tools.py`** — Tests `fetch_country_info` with mocked HTTP responses (success, 404, timeout, network errors).
- **`test_graph.py`** — Integration tests that run the full graph with mocked LLM and API calls, covering happy path, error paths, and disambiguation.

---

## Frontend (UI)

The frontend is a **Next.js 16** single-page application located in the `ui/` directory. It provides a minimal, elegant interface for querying the agent.

### How It Works

1. The user types a question (or clicks a suggested example) in the input field.
2. `page.tsx` sends a `POST` request to the backend at `${NEXT_PUBLIC_API_URL}/ask`.
3. While waiting, an animated loading indicator is shown.
4. The backend response (`{ "answer": "…" }`) is rendered in an answer card below the input.
5. Errors (network failures, server errors) are displayed inline in the same card.

### Tech Stack

- **Next.js 16** with the App Router (`src/app/`)
- **React 19** (client component with `"use client"`)
- **Tailwind CSS v4** for utility styling
- **shadcn/ui** components (card, button, input, badge, skeleton) via Radix primitives
- **Crimson Pro** + **Space Mono** Google Fonts

### Environment

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API URL (defaults to `http://localhost:8000`) |

### Running Locally

```bash
cd ui
npm install
npm run dev
# Opens at http://localhost:3000
```

The UI expects the Python backend to be running at the URL specified by `NEXT_PUBLIC_API_URL`.

### Deployment

The frontend is deployed to **Netlify** via `netlify.toml`, which builds the `ui/` directory using `npm run build` with the `@netlify/plugin-nextjs` plugin.
