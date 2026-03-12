# fraud-hunter — Infra for Government Fraud Hunters

> YC RFS Spring 2026: "Infra for Government Fraud Hunters" by Garry Tan

AI-powered toolkit for whistleblower law firms and inspectors general. Takes an insider tip, parses messy PDFs, traces corporate structures, and packages findings into complaint-ready files under the False Claims Act.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      fraud-hunter                            │
├──────────────┬───────────────┬───────────────┬──────────────┤
│  Intake      │  Processing   │  Analysis     │  Output      │
│  Pipeline    │  Engine       │  Engine       │  Generator   │
├──────────────┼───────────────┼───────────────┼──────────────┤
│ • Tip intake │ • PDF parsing │ • Entity      │ • Complaint  │
│   form       │ • OCR         │   extraction  │   drafts     │
│ • Document   │ • Table       │ • Corporate   │ • Evidence   │
│   upload     │   extraction  │   structure   │   packages   │
│ • SEC/EDGAR  │ • De-dupe     │   mapping     │ • Timeline   │
│   fetcher    │               │ • Anomaly     │   visualizer │
│ • Medicare   │               │   detection   │ • Export to  │
│   data pull  │               │ • Cross-ref   │   legal fmt  │
│              │               │   matching    │              │
└──────────────┴───────────────┴───────────────┴──────────────┘
        │               │              │               │
        ▼               ▼              ▼               ▼
   ┌──────────┐   ┌──────────┐  ┌──────────┐   ┌──────────┐
   │ Document │   │ OCR /    │  │ LLM API  │   │ Template │
   │ Storage  │   │ pdfplum- │  │ (Claude) │   │ Engine   │
   │ (S3)     │   │ ber      │  │          │   │ (Jinja2) │
   └──────────┘   └──────────┘  └──────────┘   └──────────┘
```

## Tech Stack

- **Backend**: Python + FastAPI
- **AI**: Claude API for document analysis, entity extraction, anomaly detection
- **PDF Processing**: pdfplumber + pytesseract (OCR)
- **Data**: PostgreSQL + pgvector for document search
- **Public Data**: SEC EDGAR API, Medicare provider data
- **Frontend**: Next.js (case management dashboard)

## MVP Features

1. **Tip Intake** — Structured form for whistleblower tips with anonymous submission option
2. **Document Parser** — Upload PDFs/invoices/contracts, extract text + tables + entities automatically
3. **Entity Mapper** — Trace corporate structures (subsidiaries, officers, addresses) from uploaded docs + SEC filings
4. **Anomaly Detector** — Flag suspicious patterns: billing anomalies, duplicate claims, phantom vendors
5. **Evidence Packager** — Generate complaint-ready evidence packages with timeline, entity map, and source citations

## Project Structure

```
fraud-hunter/
├── src/
│   ├── main.py                  # FastAPI app
│   ├── intake/
│   │   ├── tips.py              # Tip submission + management
│   │   └── documents.py         # Document upload + storage
│   ├── processing/
│   │   ├── pdf_parser.py        # PDF text + table extraction
│   │   ├── ocr.py               # OCR for scanned documents
│   │   └── dedup.py             # Document deduplication
│   ├── analysis/
│   │   ├── entities.py          # Entity extraction (people, orgs, amounts)
│   │   ├── corporate_map.py     # Corporate structure tracing
│   │   ├── anomaly.py           # Pattern anomaly detection
│   │   ├── cross_ref.py         # Cross-reference with public data
│   │   └── timeline.py          # Event timeline construction
│   ├── output/
│   │   ├── complaint.py         # FCA complaint draft generator
│   │   ├── evidence_pkg.py      # Evidence package builder
│   │   └── templates/           # Legal document templates
│   ├── integrations/
│   │   ├── edgar.py             # SEC EDGAR API client
│   │   └── medicare.py          # Medicare provider data
│   └── models.py                # Data models
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx             # Case dashboard
│   │   ├── cases/[id]/          # Individual case view
│   │   ├── entities/            # Entity relationship viewer
│   │   └── evidence/            # Evidence browser
│   └── package.json
├── tests/
│   ├── test_pdf_parser.py
│   ├── test_entities.py
│   ├── test_anomaly.py
│   └── fixtures/
│       ├── sample-invoice.pdf
│       └── sample-contract.pdf
├── .github/
│   └── copilot-instructions.md
├── requirements.txt
├── pyproject.toml
└── README.md
```

## rstack Workflow

```
Step 1: /plan-ceo-review
  "Review this POC for a fraud investigation toolkit. Is 'evidence
   packaging for FCA cases' the right wedge, or should we start with
   anomaly detection? What's the 10-star version for a whistleblower
   law firm?"

Step 2: /plan-eng-review
  "Review the PDF processing pipeline. How do we handle scanned docs
   vs native PDFs? What happens when entity extraction is low-confidence?
   How do we maintain chain of custody for evidence?"

Step 3: Build Phase 1 — Document Ingestion + Parsing
  - PDF parser with table extraction
  - OCR fallback for scanned documents
  - Entity extraction (names, orgs, amounts, dates)

Step 4: Build Phase 2 — Analysis Engine
  - Corporate structure mapper from SEC filings
  - Cross-reference entities across documents
  - Flag anomalies (duplicate billing, phantom vendors)

Step 5: Build Phase 3 — Evidence Packaging
  - Timeline generator
  - Complaint draft with citations
  - Export as structured evidence package

Step 6: /review
  "Review my PR. Check for: data handling of sensitive whistleblower info,
   PDF parsing edge cases (encrypted PDFs, malformed tables), and injection
   risks from extracted document text."

Step 7: /ship

Step 8: /browse http://localhost:3000
  "Upload the sample invoice and contract. Verify entities are extracted.
   Check that the evidence package includes proper citations."

Step 9: /retro
```

## Sample Output

```
┌──────────────────────────────────────────────────────────┐
│  Case: FCA-2026-0042                                     │
│  Tip: "Overbilling on Medicare DME claims"               │
│                                                          │
│  Entities Found:                                         │
│  ├── MedSupply Corp (NPI: 1234567890)                    │
│  │   ├── CEO: John Smith                                 │
│  │   ├── Subsidiary: QuickShip Medical LLC               │
│  │   └── Address: 123 Main St (matches 3 other entities) │
│  │                                                       │
│  Anomalies Detected:                                     │
│  ⚠️  142 claims for powered wheelchairs billed to        │
│     patients with no mobility diagnosis                   │
│  ⚠️  Same-day claims from 3 different addresses           │
│  ⚠️  Average claim 340% above regional median             │
│                                                          │
│  Evidence Package:                                       │
│  📄 complaint-draft.docx (FCA format)                    │
│  📊 timeline.html (interactive)                          │
│  📋 entity-map.pdf (corporate structure)                 │
│  📁 source-documents/ (12 files, chain-of-custody log)   │
└──────────────────────────────────────────────────────────┘
```
