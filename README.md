# ResearchCompass

A terminal-based, LangGraph-powered AI agent that helps **students** discover faculty and
project opportunities, and helps **professors** discover research trends, collaborators, and
research gaps — all inside a university department.

No UI. No web server. Just a fast, modular, memory-aware terminal agent.

---

## 1. Architecture

```
research-compass/
├── app.py                # Typer + Rich terminal entry point
├── config.py              # Central settings (env-driven, single source of truth)
├── requirements.txt
├── .env.example
│
├── data/
│   ├── faculty_seed.py    # Source-of-truth data for 16 faculty profiles
│   ├── faculty/           # Generated .txt documents (one per faculty member)
│   ├── trends_cache/
│   └── logs/              # SQLite DB + rotating app log
│
├── chroma_db/              # Persistent ChromaDB vector store (generated)
│
├── agents/                 # One module per LangGraph "agent" node
│   ├── router.py               # Intent classification
│   ├── student_agent.py        # Student-mode framing
│   ├── professor_agent.py      # Professor-mode framing
│   ├── retrieval.py            # RAG: semantic search + direct lookup
│   ├── trend_agent.py          # Tavily + Semantic Scholar trend search
│   ├── collaboration_agent.py  # Research-overlap collaborator suggestions
│   ├── project_agent.py        # Project suggestion engine
│   ├── gap_agent.py            # Research gap analysis
│   ├── email_agent.py          # Drafts + (on confirmation) sends email
│   ├── workload_agent.py       # Faculty capacity / overload checks
│   └── confirmation.py         # Human-in-the-loop gate
│
├── tools/                   # External-system wrappers (no LangGraph awareness)
│   ├── chroma_tool.py            # Embeddings + ChromaDB CRUD/search
│   ├── tavily_tool.py            # Tavily Search API
│   ├── semantic_scholar.py       # Semantic Scholar Graph API
│   ├── email_tool.py             # SMTP send
│   └── workload_tool.py          # Capacity math
│
├── models/                  # Pydantic + TypedDict data contracts
│   ├── faculty.py
│   ├── project.py
│   └── state.py                  # AgentState (the graph's shared memory)
│
├── graph/
│   ├── workflow.py               # StateGraph assembly + checkpointing
│   ├── nodes.py                  # Node wrappers (with conditional skip logic)
│   └── edges.py                  # Conditional routing functions
│
├── prompts/
│   └── prompts.py                # Every LLM prompt template, centralized
│
├── utils/
│   ├── helpers.py                 # LLM factory, keyword extraction, similarity
│   ├── logger.py                  # SQLite logging + file logging
│   └── ingest.py                  # Faculty seed -> .txt documents
│
├── scripts/
│   └── init_chroma.py            # One-shot ChromaDB (re)initialization
│
├── install.sh
└── run.sh
```

### Design principle: **graceful degradation**

ResearchCompass is fully runnable with **zero API keys**:

| Capability          | With API key                          | Without API key (fallback)                     |
|----------------------|----------------------------------------|-------------------------------------------------|
| Routing              | LLM-classified intent                  | Regex/keyword rule engine                       |
| Embeddings           | OpenAI embeddings (optional)           | Local `sentence-transformers` (default)         |
| Recommendation reasons| LLM-written                           | Template-generated                              |
| Trend search          | Live Tavily results + LLM summary     | Clearly-labelled offline placeholder            |
| Project/gap suggestions| LLM-generated                        | Deterministic templates                         |
| Email body            | LLM-drafted                           | Deterministic template                          |
| Email sending          | Real SMTP send                        | Logged, not sent, with a clear explanation      |

This means graders/reviewers can clone the repo, run `install.sh`, and get a fully working demo
immediately — then progressively "light up" more features by adding keys to `.env`.

---

## 2. Installation

```bash
git clone <this-repo>
cd research-compass
./install.sh
source .venv/bin/activate
python app.py chat
```

`install.sh` creates a virtualenv, installs `requirements.txt`, copies `.env.example` to `.env`,
and runs `python app.py init` to build the faculty `.txt` documents and populate ChromaDB.

## 3. Environment variables

See `.env.example` for the full list. Nothing is required to run the system; each variable
unlocks additional capability (see the fallback table above). Key ones:

- `OPENAI_API_KEY` / `OPENAI_MODEL` — enables LLM-powered routing, reasoning, summarization.
- `TAVILY_API_KEY` — enables live web trend search.
- `SEMANTIC_SCHOLAR_API_KEY` — optional, raises Semantic Scholar rate limits.
- `SMTP_HOST` / `SMTP_USER` / `SMTP_PASSWORD` — enables actual email sending.

## 4. How LangGraph is used

`graph/workflow.py` builds a `StateGraph[AgentState]` with this topology:

```
START → router → (student_mode | professor_mode) → retriever → trend_search
      → collaboration → gap_analysis → project_suggestion → confirmation
      → (email_node | END) → END
```

Every node receives and returns the same `AgentState` TypedDict (see `models/state.py`), which
is how information flows and accumulates through the pipeline. Nodes that aren't relevant to the
current query's `intent` (e.g. `collaboration` when the user asked "who works on NLP?") simply
pass the state through unchanged — cheap, and keeps the graph topology matching the specified
pipeline exactly rather than branching into many parallel graphs.

**Memory**: the graph is compiled with a `MemorySaver` checkpointer keyed by a per-session
`thread_id`, so `AgentState` (including `chat_history`) persists across turns. On top of that,
`app.py` keeps a light session memory (`last_topic`, `last_matches`) to resolve conversational
follow-ups like "show another" or "compare first two" without re-running the whole classification
pipeline.

**Human-in-the-loop**: the graph is compiled with `interrupt_before=["email_node"]`. Execution
pauses immediately before any email would be sent; `app.py` then prompts the user with
`rich.prompt.Confirm`, calls `graph.update_state(...)` with the decision, and resumes execution
with `graph.invoke(None, config)`. No email is ever sent without this explicit round-trip.

## 5. How RAG works

1. `data/faculty_seed.py` holds 16 realistic faculty profiles (Pydantic-validated via
   `models/faculty.py`).
2. `utils/ingest.py` flattens each profile into a `.txt` document under `data/faculty/`.
3. `tools/chroma_tool.py` embeds and ingests every document into a persistent ChromaDB
   collection (`chroma_db/`), using local `sentence-transformers` embeddings by default.
4. `agents/retrieval.py` handles two query shapes:
   - **Discovery** ("Who works on NLP?") → `semantic_search()` returns the top-K faculty with a
     cosine-similarity score and an LLM (or template) generated reason.
   - **Direct lookup** ("Tell me about Dr. Rao") → regex-based name extraction + exact profile
     fetch, returning the complete profile.

## 6. How ChromaDB is used

`tools/chroma_tool.py` uses `chromadb.PersistentClient` pointed at `chroma_db/`, with an
`embedding_function` chosen based on `EMBEDDING_PROVIDER`. `ingest_faculty()` is idempotent: it
only (re)builds the collection when empty or when `force=True` is passed (via
`python app.py init --force` or `python scripts/init_chroma.py --force`).

## 7. Running it

```bash
python app.py init            # one-time setup (or --force to rebuild)
python app.py chat             # interactive session
python app.py demo             # scripted demo (see below), no interaction needed
python app.py network          # bonus: faculty collaboration network tree
python app.py heatmap           # bonus: research-area coverage heatmap
```

## 8. Example conversations

### Student mode

```
You: Who works on NLP?
→ Top 5 faculty ranked by semantic similarity, with reasons and available project slots.

You: Tell me about Dr Rao.
→ Full profile: designation, projects, publications, past students, email, office, bio.

You: Suggest projects.
→ 5 project suggestions with difficulty, prerequisites, and a faculty mentor.

You: Show another.
→ Re-runs the last discovery topic (session memory) to surface fresh options.
```

### Professor mode

```
You: What's trending in AI?
→ Summary + recent sources (Tavily) + top cited papers (Semantic Scholar).

You: Who should collaborate with Dr Nair?
→ Ranked collaborators with overlap score, shared/complementary expertise, and rationale.

You: What research gaps exist?
→ Missing domains vs. current faculty coverage, with hiring/lab suggestions.

You: Generate collaboration email for Dr Nair.
→ Drafts a summary email; pauses for explicit human confirmation before ever sending via SMTP.
```

Run `python app.py demo` to see all of the above executed end-to-end automatically.

## 9. Logging

Every conversation turn and every accepted recommendation is persisted to SQLite at
`data/logs/research_compass.db` (tables: `conversations`, `recommendations`, `emails`), plus a
plain-text application log at `data/logs/app.log`.

## 10. Testing

See `tests/test_demo.py` for a scripted smoke test that exercises the full graph end-to-end
(router → retrieval → trend/collaboration/gap/project nodes) without requiring any API keys.

## 11. Notes & known limitations

- Without `TAVILY_API_KEY`, trend search returns a clearly-labelled offline placeholder rather
  than fabricated results — by design, to avoid presenting made-up "trends" as real.
- "Who should collaborate with me?" (referring to the professor as "me") requires the professor
  to be identifiable; the demo instead uses "Who should collaborate with Dr Nair?" for clarity in
  a stateless terminal session. A production deployment would resolve "me" via an authenticated
  user profile.
- Bonus visualizations (citation graph, topic similarity matrix, faculty network, heatmap) are
  rendered as Rich terminal tables/trees rather than image plots, consistent with the "everything
  runs inside the terminal, no UI" requirement.
