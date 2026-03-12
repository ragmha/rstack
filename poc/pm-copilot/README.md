# pm-copilot — Cursor for Product Managers

> YC RFS Spring 2026: "Cursor for Product Managers" by Andrew Miklas

AI-native product management tool. Upload customer interviews and usage data, ask "what should we build next?", get feature proposals backed by customer evidence — broken into tasks for your coding agent.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                    pm-copilot                           │
├─────────────┬──────────────┬──────────────┬────────────┤
│  Ingestion  │  Analysis    │  Generation  │  Export    │
│  Pipeline   │  Engine      │  Engine      │  Layer    │
├─────────────┼──────────────┼──────────────┼────────────┤
│ • Interview │ • Sentiment  │ • Feature    │ • GitHub   │
│   transcripts│  clustering │   proposals  │   Issues  │
│ • Usage     │ • Pain point │ • PRD drafts │ • Linear  │
│   analytics │   extraction │ • UI mocks   │ • Markdown │
│ • Support   │ • Theme      │ • Task       │ • Copilot  │
│   tickets   │   mapping    │   breakdown  │   prompts │
│ • Surveys   │ • Priority   │              │           │
│             │   scoring    │              │           │
└─────────────┴──────────────┴──────────────┴────────────┘
        │              │              │            │
        ▼              ▼              ▼            ▼
   ┌─────────┐   ┌──────────┐  ┌─────────┐  ┌─────────┐
   │ Storage │   │ LLM API  │  │ LLM API │  │ GitHub  │
   │ (SQLite │   │ (Claude/ │  │ (Claude/ │  │ API /   │
   │  + S3)  │   │  GPT)    │  │  GPT)   │  │ Linear  │
   └─────────┘   └──────────┘  └─────────┘  └─────────┘
```

## Tech Stack

- **Backend**: Python + FastAPI
- **AI**: Claude API (Anthropic) for analysis + generation
- **Storage**: SQLite (local POC) + S3-compatible for files
- **Frontend**: Next.js (simple dashboard)
- **Export**: GitHub Issues API, Markdown

## MVP Features

1. **Interview Ingestion** — Upload transcript files (txt, md, pdf), auto-extract customer quotes and pain points
2. **Theme Clustering** — Group pain points into themes, rank by frequency and severity
3. **Feature Proposal Engine** — Generate feature proposals backed by specific customer evidence
4. **Task Breakdown** — Break features into dev tasks formatted for coding agents (GitHub Issues with Copilot-ready descriptions)
5. **Evidence Trail** — Every proposal links back to the original customer quotes

## Setup

```bash
# Prerequisites: Python 3.11+, Node.js 18+
pip install -r requirements.txt
cd frontend && npm install

# Set API keys
export ANTHROPIC_API_KEY=your_key

# Run
uvicorn src.main:app --reload          # Backend on :8000
cd frontend && npm run dev              # Frontend on :3000
```

## Project Structure

```
pm-copilot/
├── src/
│   ├── main.py                 # FastAPI app
│   ├── ingestion/
│   │   ├── parser.py           # Transcript/file parsing
│   │   └── extractor.py        # Pain point extraction via LLM
│   ├── analysis/
│   │   ├── clustering.py       # Theme clustering
│   │   ├── scoring.py          # Priority scoring
│   │   └── evidence.py         # Evidence linking
│   ├── generation/
│   │   ├── proposals.py        # Feature proposal generation
│   │   ├── prd.py              # PRD draft generation
│   │   └── tasks.py            # Task breakdown for coding agents
│   ├── export/
│   │   ├── github.py           # GitHub Issues export
│   │   └── markdown.py         # Markdown export
│   └── models.py               # Data models
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx            # Dashboard
│   │   ├── interviews/         # Interview management
│   │   ├── themes/             # Theme explorer
│   │   └── proposals/          # Feature proposals
│   └── package.json
├── tests/
│   ├── test_parser.py
│   ├── test_clustering.py
│   └── test_proposals.py
├── sample-data/
│   ├── interview-1.md          # Sample transcript
│   ├── interview-2.md
│   └── survey-results.csv
├── .github/
│   └── copilot-instructions.md # rstack skills configured
├── requirements.txt
├── pyproject.toml
└── README.md
```

## rstack Workflow

```
Step 1: /plan-ceo-review
  "Review this POC for a Cursor-for-PMs tool. Is 'feature proposal from
   interviews' the right wedge? What's the 10-star version?"

Step 2: /plan-eng-review
  "Review the architecture. How should we handle large transcripts?
   What's the clustering strategy? What are the failure modes if the
   LLM misclassifies a pain point?"

Step 3: Build Phase 1 — Ingestion + Extraction
  - Parse transcripts, extract pain points via LLM
  - Store in SQLite with embeddings

Step 4: Build Phase 2 — Clustering + Proposals
  - Cluster pain points into themes
  - Generate feature proposals with evidence

Step 5: Build Phase 3 — Export
  - Export as GitHub Issues with Copilot-ready task descriptions

Step 6: /review
  "Review my PR. Check for LLM prompt injection in user transcripts,
   rate limiting on API calls, and data validation."

Step 7: /ship

Step 8: /browse http://localhost:3000
  "Upload the sample interviews, verify themes are extracted,
   check that proposals link back to evidence."

Step 9: /retro
```

## Sample Interaction

```
User uploads 5 customer interview transcripts

pm-copilot analyzes and outputs:

┌──────────────────────────────────────────────────────────┐
│  Theme: "Can't find relevant reports" (mentioned 4/5)    │
│  Severity: HIGH | Frequency: 80%                         │
│                                                          │
│  Evidence:                                               │
│  • "I spend 20 min every morning hunting for the right   │
│    dashboard" — Sarah, Acme Corp                         │
│  • "We have 200 reports and no one knows which ones      │
│    matter" — Mike, Beta Inc                              │
│                                                          │
│  Proposed Feature: Smart Report Discovery                │
│  "AI-powered search + recommendation engine for reports. │
│   Auto-surfaces relevant reports based on role, recent   │
│   activity, and team context."                           │
│                                                          │
│  Tasks for Copilot:                                      │
│  1. Add vector search to reports table                   │
│  2. Build role-based recommendation engine               │
│  3. Add "suggested reports" section to dashboard         │
│  4. Track report usage for relevance scoring             │
└──────────────────────────────────────────────────────────┘
```
