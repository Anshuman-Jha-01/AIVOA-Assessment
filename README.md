# AIVOA — AI-Powered Customer Complaint Management System

An AI-assisted Customer Complaint Management module for pharmaceutical API & FDF
manufacturers, built for the AIVOA Round 1 Full Stack Developer Assessment.

A QA user pastes a raw customer email or uploads a complaint PDF into the **AIVOA
Copilot** chat panel. A **LangGraph** agent (backed by **Groq**-hosted LLMs) extracts
structured complaint data, runs an initial risk assessment, checks for missing
information, flags possible duplicate complaints, suggests a probable root cause and
a draft CAPA, and writes a short executive summary — all before the QA user reviews
and commits the record to the QMS ledger.

---

## 1. Tech stack

| Layer            | Technology                                            |
|-------------------|--------------------------------------------------------|
| Frontend          | React + Redux Toolkit (Vite), Google Inter font        |
| Backend           | Python, FastAPI                                        |
| AI orchestration  | LangGraph                                               |
| LLMs              | Groq — `llama-3.3-70b-versatile` (primary), `gemma2-9b-it` (fallback) |
| Database          | PostgreSQL (MySQL also supported via SQLAlchemy)        |

---

## 2. Project structure

```
aivoa-complaints/
├── backend/
│   ├── app/
│   │   ├── agent/            # LangGraph graph, nodes, prompts, state
│   │   │   ├── state.py
│   │   │   ├── prompts.py
│   │   │   ├── nodes.py
│   │   │   └── graph.py
│   │   ├── api/               # FastAPI routers
│   │   │   ├── complaints.py  # CRUD + dashboard stats
│   │   │   └── copilot.py     # chat + file upload -> agent
│   │   ├── core/               # config + DB session
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Groq client, PDF parsing, duplicate lookup
│   │   ├── seed_data.py        # optional: seeds sample complaints
│   │   └── main.py             # FastAPI app entrypoint
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/client.js               # all backend calls
│   │   ├── app/store.js                # Redux store
│   │   ├── features/
│   │   │   ├── complaints/             # form + Redux slice + page
│   │   │   ├── copilot/                # chat panel + Redux slice
│   │   │   └── dashboard/              # KPI cards + table + Redux slice
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── samples/                    # sample complaint email/PDF for demoing
├── docker-compose.yml          # local Postgres
└── README.md
```

---

## 3. Architecture

```
┌──────────────────────────┐        REST/JSON        ┌───────────────────────────────┐
│  React + Redux (frontend)│  ───────────────────▶  │  FastAPI (backend)              │
│  • Dashboard (KPIs+table)│  ◀───────────────────  │  • /api/complaints (CRUD)        │
│  • Log Complaint form    │                          │  • /api/copilot (chat/upload)    │
│  • AIVOA Copilot chat    │                          │  • SQLAlchemy ORM → Postgres     │
└──────────────────────────┘                          │  • LangGraph agent (→ Groq LLMs) │
                                                        └───────────────────────────────┘
```

**Why this shape?** The frontend never talks to Groq directly — every AI call goes
through the FastAPI backend, which runs the LangGraph agent and returns a single
structured `CopilotResponse` (chat reply + extracted fields + risk assessment +
duplicate warnings). The React form is a "dumb" renderer of whatever fields Redux
currently holds; the AI agent is the only thing that fills them in.

---

## 4. The LangGraph agent

```
                          START
                            │
                     classify_intent
                            │
        ┌───────────────────┼────────────────────┐
   "new_complaint"      "correction"          "chit_chat"
        │                    │                    │
  extract_fields      apply_correction         chit_chat
        │                    │                    │
 check_completeness         END                   END
        │
   classify_risk
        │
  detect_duplicates
        │
  suggest_root_cause
        │
    suggest_capa
        │
     summarize
        │
compose_new_complaint_reply
        │
        END
```

Each box is one node in `backend/app/agent/nodes.py` — a small function that makes
one Groq call (JSON-mode, so the response is always structured) and returns the
state updates for that step. `backend/app/agent/graph.py` only wires the nodes
together with `langgraph.graph.StateGraph`; it contains no business logic itself.

**Why route on intent first?** The demo shows two very different interaction
patterns:
1. Pasting a full complaint (or uploading a PDF) → needs the **full pipeline**
   (extraction → completeness → risk → duplicates → root cause → CAPA → summary).
2. A short follow-up like *"ah sorry, the batch number is BMX240602"* → should
   **only** patch the mentioned field(s), not re-run the whole pipeline. This is
   the `apply_correction` node — a single cheap LLM call that diffs the message
   against the current fields.

A third `chit_chat` path handles greetings / "what can you do" questions without
touching the LangGraph pipeline at all.

### Bonus AI features implemented
All of these are LangGraph nodes, run automatically for every new complaint:
- **Completeness Checker** — `check_completeness` flags missing critical fields
- **AI Risk Classification** — `classify_risk` (Critical/Major/Minor + suggested next action)
- **Duplicate Complaint Detection** — `detect_duplicates` compares against the last 25 complaints
- **Root Cause Recommendation** — `suggest_root_cause`
- **CAPA Recommendation** — `suggest_capa`
- **Complaint Summary** — `summarize`

---

## 5. Setup & running locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for Postgres) — or a local Postgres/MySQL install
- A free Groq API key: https://console.groq.com/keys

### 5.1 Start the database

**Option A — Postgres via Docker (no local install needed):**
- Add the following to the requirements.txt file: ```psycopg2-binary==2.9.9```
```bash
docker compose up -d
```
This starts Postgres on `localhost:5432` with database `aivoa_complaints`,
user `aivoa_user`, password `aivoa_pass` (see `docker-compose.yml`).

**Option B — use a MySQL server you already have installed:**
Skip `docker compose` entirely. Just create the database/user:
```sql
CREATE DATABASE aivoa_complaints CHARACTER SET utf8mb4;
CREATE USER 'aivoa_user'@'localhost' IDENTIFIED BY 'aivoa_pass';
GRANT ALL PRIVILEGES ON aivoa_complaints.* TO 'aivoa_user'@'localhost';
FLUSH PRIVILEGES;
```
Then in `.env`, use:
```
DATABASE_URL=mysql+pymysql://aivoa_user:aivoa_pass@localhost:3306/aivoa_complaints
```
`requirements.txt` already includes `pymysql` and `cryptography` (needed for
MySQL 8's default auth plugin), so no extra install steps are required.

### 5.2 Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here

uvicorn app.main:app --reload --port 8000
```
Tables are created automatically on first run. Visit http://localhost:8000/docs
for interactive API docs.

**Optional — seed sample data** so the dashboard isn't empty:
```bash
python -m app.seed_data
```

### 5.3 Frontend
```bash
cd frontend
npm install
npm run dev
```
Visit http://localhost:5173. Vite proxies `/api/*` to `http://localhost:8000`
(see `vite.config.js`), so both servers need to be running.

### 5.4 Try it out
1. Go to **Log Customer Complaint**.
2. Paste one of the sample emails from `samples/` into the AIVOA Copilot chat box,
   or upload `samples/Zenith_Life_Sciences_Complaint_CC-2026-00154.pdf`.
3. Watch the form auto-populate and the AI risk panel appear.
4. Try a correction message, e.g. *"actually the batch number is XYZ123"*.
5. Click **Commit to QMS Ledger** and check the Dashboard.

---

## 6. Data model

| Table              | Purpose                                                        |
|---------------------|------------------------------------------------------------------|
| `complaints`         | The core QMS record — all form fields + AI assessment fields   |
| `attachments`        | Uploaded PDFs/emails and their extracted text                  |
| `copilot_messages`   | Chat history per session (for the Copilot panel)                |
| `duplicate_matches`  | AI-detected potential duplicate complaints                     |
| `audit_log`          | Append-only trail of ledger commits & field edits (traceability)|

---

## 7. Key design decisions

- **Shared field schema across LLM ⇄ API ⇄ frontend.** `ComplaintFields` in
  `schemas/complaint.py` is the single source of truth for field names, reused by
  the extraction prompt, the API contract, and (implicitly) the Redux slice —
  so there's no field-name drift between the AI output and the form.
- **JSON-mode everywhere.** Every Groq call that needs structured data uses
  `response_format: json_object`, with a defensive parser (`chat_completion_json`)
  that strips markdown fences if the model adds them anyway.
- **Model fallback.** `groq_client.py` retries on `llama-3.3-70b-versatile` if the
  primary `gemma2-9b-it` call fails, so a transient error or rate limit on the
  small model doesn't break the whole pipeline.
- **Correction path is cheap by design.** Re-running full extraction on every chat
  message would be slow and could overwrite already-correct fields. The intent
  router sends short follow-ups straight to a single-purpose `apply_correction`
  node that only touches the field(s) mentioned.
- **No OCR.** Per the assignment note, PDF parsing is plain text extraction
  (`pypdf`), not production-grade OCR — sufficient for text-based complaint PDFs.
- **Audit log table.** Even though the assignment doesn't require full 21 CFR
  Part 11 compliance, an append-only `audit_log` table was added because
  traceability is central to what a Customer Complaint module in a real QMS
  is for.

---

## 8. Sample data

`samples/` contains ready-to-use demo inputs:
- `sample_complaint_email_1.txt` — discolored capsules complaint (Major severity)
- `sample_complaint_email_2.txt` — foreign matter in API drum (Critical severity)
- `Zenith_Life_Sciences_Complaint_CC-2026-00154.pdf` — a generated sample PDF complaint report
- `make_sample_pdf.py` — regenerate/customize the sample PDF

---

## 9. What's not implemented (out of scope for this assessment)
- Authentication/authorization (single implicit QA user)
- Production-grade OCR for scanned/image-based PDFs
- Alembic migrations (tables are created via `Base.metadata.create_all` — fine for
  an assessment; a real deployment would use Alembic for schema versioning)
- Real embedding-based duplicate search (currently LLM-based comparison against
  the last 25 complaints, which is simple and effective at this data scale but
  wouldn't scale to a large complaint history)
