# rstack Examples

Real-world scenarios showing each skill running autonomously. Copy any prompt below into Copilot CLI, VS Code agent mode, or the coding agent.

---

## `/plan-ceo-review` — Product Thinking

### Example 1: Feature Request Expansion
```
I want to add a "share via email" button to our dashboard reports.
Use /plan-ceo-review to review this plan.
```
**What happens:** The skill challenges whether "share via email" is the real feature. It explores: Should reports auto-send on a schedule? Should recipients get a live link instead of a static PDF? Should we track who opened the report? It maps the 10-star version and asks you to pick SCOPE EXPANSION, HOLD, or REDUCTION.

### Example 2: New Product Direction
```
We're building an internal tool for our sales team to track customer calls.
Here's the plan: a simple CRUD app with a calls table, notes field, and date filter.
Use /plan-ceo-review in SCOPE EXPANSION mode.
```
**What happens:** The skill asks whether "call tracking" is the real job. Maybe the real product is "never lose context on a customer." It explores: auto-transcription, sentiment analysis, CRM integration, deal-stage correlation, team coaching insights.

### Example 3: Scope Reduction
```
Our plan has 47 user stories for the v2 launch. We have 3 weeks.
Here's the plan document: [paste or reference plan.md]
Use /plan-ceo-review in SCOPE REDUCTION mode.
```
**What happens:** The skill identifies the 5-7 stories that deliver 80% of the value, creates a "NOT in scope" list with rationale for each deferral, and maps what the stripped-down version still achieves.

---

## `/plan-eng-review` — Architecture & Engineering

### Example 4: API Design Review
```
I'm planning a webhook system. Merchants register URLs, we POST events to them
with retry logic. Here's my plan:
- webhooks table (url, secret, events, active)
- background job per event
- 3 retries with exponential backoff
- HMAC signature verification

Use /plan-eng-review.
```
**What happens:** The skill runs Step 0 (scope challenge), then walks through Architecture (what happens at 10k webhooks/min?), Code Quality (DRY concerns if retry logic is duplicated), Tests (diagram of all event paths including partial failures), and Performance (N+1 on webhook lookups, connection pooling for outbound HTTP). Produces ASCII diagrams of the event flow and retry state machine.

### Example 5: Database Migration Review
```
I need to add multi-tenancy to our existing single-tenant Rails app.
Plan: add tenant_id to all tables, add default_scope, update all queries.

Use /plan-eng-review as a BIG CHANGE.
```
**What happens:** The skill flags this as touching 30+ files, challenges whether `default_scope` is the right approach (it has known footguns), diagrams the migration path for existing data, maps failure modes (what if a query leaks across tenants?), and produces a test matrix covering tenant isolation.

---

## `/review` — Pre-Landing PR Review

### Example 6: Review a Feature Branch
```
/review
```
**What happens (on a feature branch):** Detects the default branch, fetches latest, runs `git diff`, reads the multi-stack checklist, and does a two-pass review. Example output:
```
Pre-Landing Review: 3 issues (1 critical, 2 informational)

CRITICAL (blocking):
- [src/api/webhooks.ts:42] SQL injection via string interpolation in webhook URL filter
  Fix: Use parameterized query: db.query('SELECT * FROM webhooks WHERE url = ?', [url])

Issues (non-blocking):
- [src/api/webhooks.ts:78] Missing error handling for HTTP timeout on webhook delivery
  Fix: Add try/catch with specific timeout error, log to monitoring
- [src/api/webhooks.ts:15] Magic number 3 for retry count — extract to WEBHOOK_MAX_RETRIES constant
  Fix: const WEBHOOK_MAX_RETRIES = 3
```

### Example 7: Review with Auto-Fix
```
Review my PR. If you find critical issues, fix them automatically.
```
**What happens:** Same as above, but for each CRITICAL issue it presents options. If running autonomously (coding agent), it auto-picks "Fix now" for critical issues, applies the fixes, and commits them.

---

## `/ship` — Automated Shipping

### Example 8: Ship a Node.js Project
```
/ship
```
**What happens (on a feature branch in a Node.js project):**
1. Detects `main` as default branch
2. Runs `git fetch origin main && git merge origin/main`
3. Detects `package.json` + `package-lock.json` → runs `npm test`
4. Reads review checklist, runs pre-landing review
5. Detects `package.json` version → bumps `1.2.3` → `1.2.4`
6. Detects `CHANGELOG.md` → auto-generates entry from commits
7. Commits in bisectable chunks
8. Pushes and runs `gh pr create`
9. Outputs: `https://github.com/you/repo/pull/42`

### Example 9: Ship a Python Project
```
Ship this branch. We don't have a VERSION file or CHANGELOG.
```
**What happens:**
1. Detects `main`, merges it
2. Detects `pyproject.toml` → runs `pytest`
3. Runs pre-landing review
4. No VERSION file → skips versioning
5. No CHANGELOG.md → skips changelog
6. Commits, pushes, opens PR with test results
7. Outputs PR URL

### Example 10: Ship a Go Monorepo
```
/ship
```
**What happens:**
1. Detects `go.mod` → runs `go test ./...`
2. Runs review (Go-specific: checks for goroutine leaks, defer misuse)
3. No version file → skips
4. Pushes, opens PR

---

## `/browse` — Browser QA

### Example 11: Verify a Deployment
```
/browse staging.myapp.com — check that the homepage loads, there are no console
errors, and the login flow works with test@example.com / password123
```
**What happens:**
```
> browse goto https://staging.myapp.com
Navigated to https://staging.myapp.com (200)

> browse console
No console errors.

> browse screenshot /tmp/homepage.png
[screenshot saved]

> browse snapshot -i
[interactive elements listed with @refs]

> browse click @e4                    (Login link)
> browse fill @e7 "test@example.com"
> browse fill @e8 "password123"
> browse click @e9                    (Submit)
> browse screenshot /tmp/after-login.png
[screenshot saved]

> browse url
https://staging.myapp.com/dashboard

> browse console
No console errors.

Homepage loads. Login works. Redirected to dashboard. No JS errors.
```

### Example 12: Responsive Layout Check
```
Browse our marketing site at https://mysite.com and check the layout
at mobile, tablet, and desktop widths. Screenshot each.
```
**What happens:**
```
> browse goto https://mysite.com
> browse responsive /tmp/mysite
  Saved: /tmp/mysite-mobile-375x812.png
  Saved: /tmp/mysite-tablet-768x1024.png
  Saved: /tmp/mysite-desktop-1440x900.png

[reads each screenshot]
Mobile: hamburger menu renders, hero text wraps correctly.
Tablet: sidebar collapses, two-column grid intact.
Desktop: full navigation bar, three-column layout.
No broken layouts detected.
```

### Example 13: Fill and Submit a Form
```
/browse https://myapp.com/signup — create a test account with
name "Test User", email "test-bot@example.com", password "Test1234!"
and verify the confirmation page.
```
**What happens:** Navigates to signup, uses `snapshot -i` to find form fields, fills each by ref, submits, screenshots the result, checks for success message.

---

## `/retro` — Engineering Retrospective

### Example 14: Weekly Retro
```
/retro
```
**What happens:**
```
Week of Mar 8: 32 commits, 2.1k LOC, 35% tests, 8 PRs, peak: 9pm | Streak: 12d

## Engineering Retro: Mar 5 – Mar 12

### Summary Table
| Metric              | Value  |
|---------------------|--------|
| Commits to main     | 32     |
| PRs merged          | 8      |
| Net LOC added       | 1,400  |
| Test LOC ratio      | 35%    |
| Active days          | 5      |
| Detected sessions   | 11     |
| Avg LOC/session-hour| 250    |

### Time & Session Patterns
Peak coding: 8-11pm (after meetings clear out). 3 deep sessions (50+ min),
5 medium, 3 micro. ~4.5 hours active coding per day.

### Top 3 Wins
1. Webhook system shipped end-to-end (650 LOC, 12 commits)
2. Fixed the N+1 query in dashboard load (2.3s → 180ms)
3. Added retry logic with exponential backoff for all external APIs

### 3 Things to Improve
1. Test ratio dropped from 42% to 35% — webhook tests are thin
2. 3 XL PRs this week (1500+ LOC) — split earlier next time
3. Two fix-chains on the same file (api/webhooks.ts) — review before merge
```

### Example 15: Compare Mode
```
/retro compare
```
**What happens:** Computes metrics for this week and last week, shows side-by-side:
```
                  Last Week    This Week    Delta
Commits:          24      →    32           ↑33%
Test ratio:       42%     →    35%          ↓7pp
Deep sessions:    2       →    3            ↑1
Fix ratio:        58%     →    38%          ↓20pp (improving)
Streak:           5d      →    12d          ↑7d
```

---

## Combined Workflows (Multi-Skill)

### Example 16: Full Feature Cycle
```
Step 1: "I want to add real-time notifications to our app.
         Use /plan-ceo-review to review this idea."

Step 2: "Good, I like the expanded vision. Now use /plan-eng-review
         to lock in the architecture."

Step 3: [implement the plan]

Step 4: "/review"

Step 5: [fix any critical issues]

Step 6: "/ship"

Step 7: "/browse staging.myapp.com — verify notifications appear
         when I trigger a test event"
```

### Example 17: Coding Agent on GitHub (Autonomous)
Open an issue on GitHub:
```
Title: Add CSV export to the reports page

Body: Users need to download their monthly reports as CSV files.
      Use /plan-eng-review to plan the implementation, then build it,
      run /review, and /ship when ready.
```
**What happens (Copilot coding agent):** Creates a branch, runs eng review (auto-picks recommended options since no interactive user), implements the plan, runs review, ships the PR — all from an issue assignment.

### Example 18: Quick Bug Fix
```
There's a bug: users see a blank page when their report has zero rows.
Fix it and /ship.
```
**What happens:** Copilot finds the bug, fixes it, then `/ship` kicks in: merges main, runs tests, does a quick review (catches if the fix introduced any new issues), bumps patch version, pushes, opens PR.
