# gov-ai — AI for Government Form Processing

> YC RFS Spring 2026: "AI for Government" by Tom Blomfield

AI-powered form and application processing for local, state, and federal government agencies. Handles the receiving end — turning the flood of citizen submissions into structured, actionable data with automated review and routing.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         gov-ai                                │
├──────────────┬───────────────┬───────────────┬───────────────┤
│  Intake      │  Processing   │  Review       │  Action       │
│  Gateway     │  Pipeline     │  Engine       │  Layer        │
├──────────────┼───────────────┼───────────────┼───────────────┤
│ • API for    │ • Form field  │ • Completeness│ • Auto-approve│
│   digital    │   extraction  │   check       │   (rules)     │
│   submissions│ • Document    │ • Eligibility │ • Route to    │
│ • PDF/scan   │   classifica- │   pre-screen  │   reviewer    │
│   upload     │   tion        │ • Fraud signal│ • Request     │
│ • Email      │ • Data        │   detection   │   more info   │
│   intake     │   validation  │ • Priority    │ • Decision    │
│ • Bulk batch │ • De-dupe     │   scoring     │   letter gen  │
│   processing │               │               │               │
└──────────────┴───────────────┴───────────────┴───────────────┘
        │               │              │               │
        ▼               ▼              ▼               ▼
   ┌──────────┐   ┌──────────┐  ┌──────────┐   ┌──────────┐
   │ Document │   │ LLM API  │  │ Rules    │   │ Notifica-│
   │ Store    │   │ (Claude) │  │ Engine   │   │ tion Svc │
   │ (S3)     │   │          │  │ (custom) │   │ (email)  │
   └──────────┘   └──────────┘  └──────────┘   └──────────┘
```

## Tech Stack

- **Backend**: Python + FastAPI
- **AI**: Claude API for form extraction, classification, eligibility screening
- **Rules Engine**: Custom Python rules (configurable per agency/form type)
- **Queue**: Redis + Celery for async processing
- **Storage**: PostgreSQL + S3 for documents
- **Frontend**: Next.js (reviewer dashboard)

## MVP Features

1. **Form Intake API** — Accept digital submissions (JSON, PDF, scanned images) via API or upload
2. **Smart Extraction** — Extract structured data from unstructured forms (handwritten, PDF, scanned)
3. **Completeness Check** — Flag missing required fields, invalid data, inconsistencies
4. **Eligibility Pre-Screen** — Based on extracted data + rules, auto-determine likely eligibility
5. **Reviewer Dashboard** — Queue of applications ranked by priority, with AI-extracted summaries

## Project Structure

```
gov-ai/
├── src/
│   ├── main.py                  # FastAPI app
│   ├── intake/
│   │   ├── api.py               # Submission API endpoints
│   │   ├── email.py             # Email intake processor
│   │   └── batch.py             # Bulk batch processing
│   ├── processing/
│   │   ├── extractor.py         # Form field extraction via LLM
│   │   ├── classifier.py        # Document type classification
│   │   ├── validator.py         # Data validation + normalization
│   │   └── dedup.py             # Duplicate submission detection
│   ├── review/
│   │   ├── completeness.py      # Missing field detection
│   │   ├── eligibility.py       # Rule-based eligibility screening
│   │   ├── fraud.py             # Fraud signal detection
│   │   └── priority.py          # Priority queue scoring
│   ├── action/
│   │   ├── router.py            # Route to appropriate reviewer
│   │   ├── auto_approve.py      # Auto-approval for clean apps
│   │   ├── notifications.py     # Status notifications
│   │   └── letters.py           # Decision letter generation
│   ├── rules/
│   │   ├── engine.py            # Configurable rules engine
│   │   └── templates/           # Rule sets per form type
│   └── models.py
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx             # Reviewer dashboard
│   │   ├── applications/[id]/   # Individual application
│   │   ├── queue/               # Review queue
│   │   └── analytics/           # Processing metrics
│   └── package.json
├── tests/
│   ├── test_extractor.py
│   ├── test_eligibility.py
│   ├── test_rules_engine.py
│   └── fixtures/
│       ├── sample-permit-app.pdf
│       └── sample-benefits-form.pdf
├── .github/
│   └── copilot-instructions.md
├── requirements.txt
├── pyproject.toml
└── README.md
```

## rstack Workflow

```
Step 1: /plan-ceo-review
  "Review this POC for government form processing AI. Should we start
   with a specific form type (building permits? benefits applications?)
   or build a general-purpose engine? What's the 10-star version for
   a county clerk's office drowning in paper?"

Step 2: /plan-eng-review
  "Review the processing pipeline. How do we handle handwritten forms?
   What's the accuracy threshold for auto-approval? How do we audit
   AI decisions for compliance? What about PII handling?"

Step 3: Build Phase 1 — Intake + Extraction
  - PDF upload endpoint
  - LLM-powered form field extraction
  - Structured data output

Step 4: Build Phase 2 — Review Engine
  - Completeness checker
  - Rules-based eligibility screening
  - Priority queue

Step 5: Build Phase 3 — Dashboard
  - Reviewer queue with AI summaries
  - Application detail view
  - Processing metrics

Step 6: /review
  "Review my PR. Check for: PII exposure in logs, extraction accuracy
   edge cases (blurry scans, multi-page forms), and rule engine
   bypass risks."

Step 7: /ship

Step 8: /browse http://localhost:3000
  "Upload the sample permit application. Verify fields are extracted.
   Check the reviewer queue shows it with correct priority."

Step 9: /retro
```

## Sample Interaction

```
Agency uploads 50 building permit applications (PDFs)

gov-ai processes and shows:

┌──────────────────────────────────────────────────────────┐
│  Processing Complete: 50 applications                    │
│                                                          │
│  ✅ Auto-approved: 12 (complete, meets all requirements) │
│  ⏳ Ready for review: 31 (needs human check)             │
│  ⚠️  Needs more info: 5 (missing required docs)          │
│  🚫 Flagged: 2 (potential duplicate / inconsistency)     │
│                                                          │
│  Review Queue (sorted by priority):                      │
│  ┌────┬──────────────┬──────────┬──────────┬──────────┐  │
│  │ #  │ Applicant    │ Type     │ Status   │ Score    │  │
│  ├────┼──────────────┼──────────┼──────────┼──────────┤  │
│  │ 1  │ ABC Builders │ Commer.  │ 🚫 Flag  │ 95       │  │
│  │ 2  │ Smith Reno   │ Resid.   │ ⏳ Review │ 82       │  │
│  │ 3  │ Quick Build  │ Resid.   │ ⏳ Review │ 78       │  │
│  └────┴──────────────┴──────────┴──────────┴──────────┘  │
│                                                          │
│  Time saved: ~40 hours of manual data entry              │
└──────────────────────────────────────────────────────────┘
```
