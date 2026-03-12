# ai-agency — AI-Native Agency Platform

> YC RFS Spring 2026: "AI-Native Agencies" by Aaron Epstein

Platform for running AI-powered service businesses at software margins. Instead of selling software for clients to use, you use AI to do the work and sell the finished product — design, ad creative, legal docs, content — at premium prices with near-zero marginal cost.

## Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                       ai-agency                                │
├───────────────┬───────────────┬───────────────┬───────────────┤
│  Client       │  Workflow     │  AI Workers   │  Delivery     │
│  Portal       │  Engine       │               │  Pipeline     │
├───────────────┼───────────────┼───────────────┼───────────────┤
│ • Project     │ • Template    │ • Copywriter  │ • Review      │
│   intake form │   library     │ • Designer    │   queue       │
│ • Brief       │ • Stage       │ • Video editor│ • Revision    │
│   builder     │   management  │ • Legal writer│   tracker     │
│ • Asset       │ • Auto-assign │ • Researcher  │ • Client      │
│   upload      │   to AI worker│ • Analyst     │   approval    │
│ • Feedback    │ • Human QA    │               │ • Export /    │
│   loop        │   checkpoints │               │   delivery    │
└───────────────┴───────────────┴───────────────┴───────────────┘
        │               │              │               │
        ▼               ▼              ▼               ▼
   ┌──────────┐   ┌──────────┐  ┌──────────┐   ┌──────────┐
   │ Project  │   │ Workflow  │  │ LLM APIs │   │ Storage  │
   │ Database │   │ Queue    │  │ (Claude,  │   │ (S3 for  │
   │ (Postgres│   │ (Redis)  │  │  GPT,     │   │  assets) │
   │          │   │          │  │  DALL-E)  │   │          │
   └──────────┘   └──────────┘  └──────────┘   └──────────┘
```

## Tech Stack

- **Backend**: Python + FastAPI
- **AI**: Claude (copy/legal), GPT-4 (analysis), DALL-E/Midjourney API (design)
- **Queue**: Redis + Celery for async AI workers
- **Storage**: PostgreSQL + S3 for client assets
- **Frontend**: Next.js (client portal + admin dashboard)

## MVP Features — Ad Agency Vertical

Start with one vertical: **AI ad creative agency**.

1. **Brief Builder** — Client fills structured creative brief (brand, audience, goals, tone, assets)
2. **Creative Pipeline** — AI generates ad copy, headlines, CTAs in multiple variations
3. **Visual Generation** — AI creates ad visuals from brief + brand assets
4. **Variation Matrix** — Generate A/B test variations across copy × visual × format
5. **Review Dashboard** — Internal QA queue before client delivery
6. **Client Portal** — Client reviews, approves, requests revisions

## Project Structure

```
ai-agency/
├── src/
│   ├── main.py                  # FastAPI app
│   ├── client/
│   │   ├── intake.py            # Brief builder + project intake
│   │   ├── portal.py            # Client-facing portal API
│   │   └── feedback.py          # Revision request handling
│   ├── workflow/
│   │   ├── engine.py            # Workflow stage management
│   │   ├── templates.py         # Project templates (ad, legal, design)
│   │   └── assignment.py        # Auto-assign to AI workers
│   ├── workers/
│   │   ├── copywriter.py        # Ad copy generation
│   │   ├── designer.py          # Visual generation
│   │   ├── variation.py         # A/B variation matrix
│   │   └── base.py              # Base AI worker class
│   ├── delivery/
│   │   ├── review.py            # Internal QA queue
│   │   ├── export.py            # Export in ad platform formats
│   │   └── tracking.py          # Delivery + revision tracking
│   └── models.py
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx             # Admin dashboard
│   │   ├── projects/            # Project management
│   │   ├── review/              # QA review queue
│   │   └── client/              # Client portal
│   └── package.json
├── tests/
│   ├── test_copywriter.py
│   ├── test_workflow.py
│   └── test_variations.py
├── .github/
│   └── copilot-instructions.md
├── requirements.txt
├── pyproject.toml
└── README.md
```

## rstack Workflow

```
Step 1: /plan-ceo-review
  "Review this POC for an AI ad agency platform. Should we start with
   ad copy only, or include visual generation from day 1? What's the
   10-star version — does it include performance prediction?"

Step 2: /plan-eng-review
  "Review the worker pipeline. How do we handle brand consistency across
   variations? What's the QA checkpoint architecture? How do we handle
   client revision requests without regenerating everything?"

Step 3: Build Phase 1 — Brief Builder + Copy Generation
  - Structured brief intake
  - AI copywriter worker (headlines, body copy, CTAs)
  - Multiple variations per brief

Step 4: Build Phase 2 — Visual Generation + Variations
  - Image generation from brief + brand guidelines
  - Copy × visual variation matrix
  - Format adapters (Instagram, Facebook, Google Ads)

Step 5: Build Phase 3 — Review + Delivery
  - Internal QA queue
  - Client portal with approval flow
  - Export in platform-ready formats

Step 6: /review
  "Review my PR. Check for: prompt injection from client briefs, rate
   limiting on AI API calls, brand asset handling (don't leak between
   clients), and image generation cost controls."

Step 7: /ship

Step 8: /browse http://localhost:3000
  "Create a test project with a sample brief. Verify copy variations
   are generated. Check the client portal shows the deliverables."

Step 9: /retro
```

## Unit Economics

```
Traditional Ad Agency:
  • Senior copywriter: $150/hr × 8 hrs = $1,200 per campaign
  • Designer: $120/hr × 12 hrs = $1,440 per campaign
  • Total cost: ~$2,640
  • Client price: $5,000-$15,000
  • Margin: 50-80%
  • Capacity: 10-15 campaigns/month per team

AI-Native Agency (ai-agency):
  • AI generation: ~$2-5 per campaign (API costs)
  • Human QA: $50/hr × 1 hr = $50 per campaign
  • Total cost: ~$55
  • Client price: $2,000-$5,000 (undercut traditional)
  • Margin: 97%+
  • Capacity: 500+ campaigns/month per operator

The 10-star version: AI pre-tests creative against historical
performance data and only delivers variations predicted to perform
above the client's benchmark. You charge for performance, not hours.
```
