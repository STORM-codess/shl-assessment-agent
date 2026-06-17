# SHL Assessment Recommendation Agent

A conversational agent that helps recruiters and hiring managers find the right
assessments through natural language — instead of keyword search and filters.
Ask in plain English ("I need a test for a junior Java developer, under 40
minutes"), and the agent clarifies vague requirements, recommends relevant
assessments grounded in the SHL catalog, and refines its suggestions as the
conversation evolves.

Built with **FastAPI + Groq (Llama 3.1 8B Instant)**, with a React frontend.

<!-- Add a demo GIF or screenshot here once you have one:
![demo](docs/demo.gif)
-->

**Live demo:** [https://your-app.onrender.com](https://shl-assesment-frontend.onrender.com/)

---

## Why this exists

Recruiters don't think in filters — they think in requirements: a role, a
seniority level, a time budget, a skill to test. Traditional catalog search
forces them to translate that into tags and keywords. This agent removes that
translation step: it holds a conversation, asks clarifying questions when a
request is ambiguous, and returns assessments grounded in the actual catalog
rather than the model's memory.

## What it does

- **Clarifies vague requirements** before recommending — if a request is
  underspecified, the agent asks targeted follow-up questions instead of
  guessing.
- **Catalog-grounded recommendations** — suggestions are drawn from the SHL
  assessment catalog via retrieval, not hallucinated from model memory.
- **Conversational refinement** — when requirements change mid-conversation
  ("actually, make it shorter"), the agent adjusts its recommendations.
- **Catalog-grounded comparisons** — compares assessments using real catalog
  information rather than invented details.
- **Handles out-of-scope and adversarial input** — gracefully declines
  off-topic requests and resists prompt-injection attempts.
- **Stateless architecture** — conversation state is passed in per request, so
  the service scales horizontally without sticky sessions.
- **Structured output** — recommendations return assessment names, URLs, and
  test types in a predictable schema.

## Architecture

```
User ──▶ React frontend ──▶ FastAPI
                                │
                    ┌───────────┴───────────┐
                    │  Retrieval over the    │
                    │  SHL catalog           │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │  Prompt orchestration  │
                    │  + Groq (Llama 3.1 8B) │
                    └───────────┬───────────┘
                                │
                    Structured recommendations
                    (name, URL, test type)
```

The pipeline separates **retrieval** (find relevant catalog entries) from
**generation** (compose a grounded, schema-compliant response), with prompt
orchestration handling clarification, refinement, and out-of-scope detection.

## Tech stack

**Backend:** Python · FastAPI · Groq API (Llama 3.1 8B Instant) · custom
retrieval + recommendation pipeline · conversation state management

**Frontend:** React · JavaScript · Axios 

**Deployment:** Render (frontend + backend)

## API

<!-- VERIFY all paths and request/response shapes against app/ -->

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/health` | Health check |
| `POST` | `/chat` | Conversational recommendation — accepts a message + conversation state, returns structured recommendations |

Example request:

```json
POST /chat
{
  "message": "I need an assessment for a junior Java developer, max 40 minutes",
  "conversation": []
}
```

Example response (shape):

```json
{
  "reply": "Here are a few options that fit a junior Java role under 40 minutes...",
  "recommendations": [
    {
      "name": "Core Java (Entry Level)",
      "url": "https://www.shl.com/...",
      "test_type": "Knowledge & Skills"
    }
  ]
}
```


## Run locally

```bash
# clone, then:
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# set your Groq key
export GROQ_API_KEY=gsk_your_key  # Windows PowerShell: $env:GROQ_API_KEY="gsk_..."

# run the API
uvicorn app.main:app --reload     # VERIFY: actual module path
```

<!-- VERIFY: frontend run steps if the frontend is in this repo -->

## Project structure

```
app/                  # FastAPI app: routes, retrieval, prompt orchestration
data/                 # SHL catalog data
tests/                # tests
evaluation_runner.py  # offline evaluation harness
requirements.txt
runtime.txt           # Python version pin (for Render)
```

## What I learned

Reliable conversational systems are far more than "call an LLM and return the
answer." The hard parts were designing clarification strategies, handling
mid-conversation refinement, grounding every response to the catalog,
enforcing schema compliance, and keeping behaviour consistent across multi-turn
conversations — plus defending against out-of-scope and prompt-injection input.
The project also gave me hands-on experience with API design, retrieval
systems, agent orchestration, evaluation-driven development, and deployment.
