# Plan CEO Review — Examples

Reference examples for the `/plan-ceo-review` skill. These illustrate scope expansion thinking and the expected output format.

---

## Example 1: Photo Upload → Smart Listing Flow

**Original plan:** "Add multi-photo upload to product listings."

**Premise challenge:** The real problem isn't uploading photos — it's that creating a listing is slow and tedious. Photos are the bottleneck, but they're not the whole story.

**10-star version:** User points their camera at the item. The system captures photos, auto-crops, removes background, detects the item category, suggests a title and description, estimates a price from comparable listings, and creates a draft listing — all before the user types a single character.

**Scope expansion mapping:**

```
CURRENT STATE               THIS PLAN                  12-MONTH IDEAL
─────────────               ──────────                 ──────────────
Manual single upload   →    Multi-photo upload    →    Camera-to-listing in <60s
User writes all text   →    (unchanged)           →    AI-generated descriptions
No price guidance      →    (unchanged)           →    Comparable price suggestions
No image processing    →    (unchanged)           →    Auto-crop, bg removal
```

**The 2x effort / 10x impact move:** Add auto-categorization from the first photo. User uploads → system suggests category + title → user confirms or edits. This is ~2x the effort of plain multi-upload but transforms the listing experience. Everything else (AI descriptions, pricing) can follow as iterations.

---

## Example 2: TODO App → Productivity System

**Original plan:** "Build a simple TODO app with create, complete, delete."

**Premise challenge:** The world has a thousand TODO apps. Why build another? The real problem is that people don't finish tasks — they add them to lists and forget. A 10-star TODO app doesn't just store tasks, it helps you *do* them.

**10-star version:** A task system that understands context. When you add "review PR #42," it links to the PR, shows the diff size, and estimates review time. When you add "prepare for Monday standup," it pulls your last week's commits and draft PRs into a summary. Tasks have energy levels (deep work vs. quick wins) and the system suggests what to work on based on your current energy and available time.

**Scope reduction version (if chosen):**

Core outcome: "Users can capture and complete tasks." (7 words)

Keep:
- Create task (title only — no descriptions, no due dates)
- Mark complete
- List active tasks

Cut:
- Delete (complete is enough for v1)
- Categories/tags (add when users ask for it)
- Due dates (add when users miss deadlines)
- Search (not needed under 100 tasks)

---

## Example 3: Completion Summary Table Template

Every review ends with this table. It captures all decisions for quick reference.

```
## Completion Summary

| #  | Issue                          | Decision | Notes                              |
|----|--------------------------------|----------|-------------------------------------|
| 1  | Upload strategy                | A        | Batch INSERT, single transaction    |
| 2  | Image processing timing        | B        | Async via background job            |
| 3  | Error handling for S3 timeout  | A        | Retry with exponential backoff      |
| 4  | Auth on upload endpoint        | A        | Token-based, existing middleware     |
| 5  | Test coverage for edge cases   | A        | Add tests for empty/oversized files |
| 6  | Caching strategy               | C        | Deferred — low read volume for now  |
| 7  | Rate limiting                  | B        | Follow-up TODO, pre-launch          |

### Mode: SCOPE EXPANSION
### Key Insight: Multi-upload is table stakes. Auto-categorization is the differentiator.
### Net New TODOs: 3 added, 1 resolved
### Diagrams: 2 (system architecture, upload data flow)
```

The summary table is the "receipt" of the review. Anyone reading it should understand what was decided without reading the full review.
