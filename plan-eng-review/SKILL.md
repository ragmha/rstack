---
name: plan-eng-review
description: |
  Engineering plan review. Lock in architecture, data flow, diagrams, edge cases,
  and test coverage. Walks through issues interactively with opinionated
  recommendations. Use when asked for an engineering review, architecture review,
  technical review, or eng review. Trigger with /plan-eng-review.
---

# /plan-eng-review — Engineering Plan Review

Review this plan thoroughly before making any code changes. For every issue or recommendation, explain the concrete tradeoffs, give an opinionated recommendation, and ask for input before assuming a direction.

## Priority Hierarchy

If running low on context, prioritize in this order:

**Step 0 > Test diagram > Opinionated recommendations > Everything else.**

Never skip Step 0 or the test diagram.

## Engineering Preferences

- **DRY** — flag repetition aggressively
- **Well-tested** — too many tests > too few
- **"Engineered enough"** — not over-engineered, not under-engineered
- **More edge cases, not fewer** — surface them proactively
- **Explicit over clever** — readability wins
- **Minimal diff** — fewest new abstractions and files to accomplish the goal

## Diagrams

- Value ASCII art highly: data flow, state machines, dependency graphs, pipelines, decision trees
- Embed in code comments where appropriate
- Diagram maintenance is part of the change — stale diagrams are worse than none

## Step 0: Scope Challenge

Before reviewing anything, answer these questions:

1. **What existing code already solves sub-problems?** Can we reuse, not rebuild?
2. **Minimum changes for stated goal?** Flag anything deferrable.
3. **Complexity check:** >8 files touched or >2 new classes = smell. Challenge it.

Then ask the user (via `ask_user`) to pick one of:

- **A) SCOPE REDUCTION** — The plan is overbuilt. Propose a minimal version that achieves the stated goal.
- **B) BIG CHANGE** — Work through the review interactively, one section at a time, max 8 issues per section.
- **C) SMALL CHANGE** — Compressed review. One most-important issue per section, single batch.

**CRITICAL:** If the user does NOT select SCOPE REDUCTION, commit fully to their chosen scope. Do not second-guess or try to reduce scope after this point.

---

## Review Sections

### 1. Architecture Review

Evaluate:
- System design and component boundaries
- Dependency graph
- Data flow
- Scaling considerations
- Security implications
- Diagrams needed

For each new codepath: describe one realistic production failure scenario.

**STOP.** For each issue: use `ask_user` individually. One issue per call. Present 2–3 lettered options. State your recommendation FIRST. Explain WHY in one sentence, mapping back to the engineering preferences above.

### 2. Code Quality Review

Evaluate:
- Code organization
- DRY violations
- Error handling completeness
- Edge cases missed
- Tech debt introduced
- Over-engineering or under-engineering

Check ASCII diagrams in touched files — are they still accurate after this change?

**STOP.** Same `ask_user` pattern as Architecture Review.

### 3. Test Review

Make a diagram of all new UX flows, data flows, codepaths, and branching logic. For each new item in the diagram, verify there is a corresponding test.

**STOP.** Same `ask_user` pattern as Architecture Review.

### 4. Performance Review

Evaluate:
- N+1 queries
- Memory allocation patterns
- Caching opportunities
- Slow paths under load
- High-complexity code (O(n²) or worse)

**STOP.** Same `ask_user` pattern as Architecture Review.

---

## Question Format Rules

Every `ask_user` call MUST follow this format:

1. Present 2–3 concrete lettered options
2. State the recommended option FIRST
3. Explain WHY in 1–2 sentences, mapping to the engineering preferences

No batching multiple issues into one question. No yes/no questions. Use open-ended questions only for genuine ambiguity.

**Async fallback:** If running asynchronously without interactive user access, choose the recommended option and document the decision.

## For Each Issue Found

- Describe the issue concretely with file and line references
- Provide 2–3 options, always including "do nothing"
- For each option: effort estimate, risk level, maintenance burden
- Lead with your recommendation: **"Do B. Here's why:"** — not "B might be worth considering"
- If there's an obvious fix with no real alternatives, just state it and move on

## Required Outputs

### 1. "NOT in scope"

Work that was considered and explicitly deferred. One-line rationale for each item.

### 2. "What already exists"

Existing code that solves sub-problems relevant to this plan. Reference files and functions.

### 3. TODO Updates

One `ask_user` per TODO item with:
- **What:** the proposed TODO
- **Why:** motivation
- **Pros/Cons:** tradeoffs of adding it
- **Context:** where it fits in the codebase
- **Dependencies:** what it blocks or is blocked by

Options:
- **A) Add to TODOs** — track it for later
- **B) Skip** — not worth tracking
- **C) Build now** — do it as part of this change

### 4. Diagrams

Produce ASCII diagrams for all non-trivial flows. Identify files that need inline diagram comments added or updated.

### 5. Failure Modes

For each new codepath:
- One realistic failure scenario
- Is there test coverage for this failure?
- Is there error handling?
- Is the failure user-visible or silent?

### 6. Completion Summary

At the end of the review, produce this summary:

```
Step 0: user chose ___
Architecture Review: ___ issues
Code Quality Review: ___ issues
Test Review: diagram produced, ___ gaps
Performance Review: ___ issues
NOT in scope: written
What already exists: written
TODO updates: ___ items proposed
Failure modes: ___ critical gaps
```

## Formatting Rules

- **NUMBER** issues sequentially (1, 2, 3…)
- **LETTER** options within each issue (A, B, C…)
- Recommended option listed first, one sentence max per option description
- After each section, pause for feedback before continuing to the next section
