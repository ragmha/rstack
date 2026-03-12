---
name: review
description: |
  Pre-landing PR review. Analyzes the current branch diff for security issues,
  race conditions, trust boundary violations, and structural problems that tests
  don't catch. Use when asked to review a PR, review code changes, or do a
  pre-landing check. Trigger with /review.
---

You are running the `/review` workflow. Analyze the current branch's diff against the default branch for structural issues that tests don't catch.

## Step 1 — Check branch

1. Run `git branch --show-current` via the `bash` tool.
2. If you are on the default branch, output **"Nothing to review — you're on the default branch."** and stop.
3. Detect the default branch:

```bash
DEFAULT_BRANCH=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}')
DEFAULT_BRANCH=${DEFAULT_BRANCH:-main}
```

4. Run `git fetch origin $DEFAULT_BRANCH --quiet && git diff origin/$DEFAULT_BRANCH --stat` — if the diff is empty, output **"Nothing to review — no diff against the default branch."** and stop.

## Step 2 — Read the checklist

Use the `view` tool to read the checklist file. Try these paths in order:

1. `.github/skills/rstack/review/checklist.md`
2. `.github/skills/review/checklist.md`
3. `~/.copilot/skills/rstack/review/checklist.md`
4. `~/.copilot/skills/review/checklist.md`

If none of these files exist, **STOP** and report: "Could not find the review checklist. Place checklist.md in one of the expected paths."

## Step 3 — Get the diff

```bash
git fetch origin $DEFAULT_BRANCH --quiet
git diff origin/$DEFAULT_BRANCH
```

Read the **full** diff into context before proceeding.

## Step 4 — Two-pass review

Apply the checklist against the diff:

- **Pass 1 (CRITICAL):** SQL & Data Safety, Race Conditions & Concurrency, Security & Trust Boundaries
- **Pass 2 (INFORMATIONAL):** all remaining checklist categories

## Step 5 — Output findings

Always output **ALL** findings.

- **CRITICAL issues found:** For **each** critical issue, use `ask_user` with:
  - The problem (one line)
  - The recommended fix (one line)
  - Options: **A)** Fix now **B)** Acknowledge **C)** False positive
- After all critical issues are answered: if any **A)** was chosen, use the `edit` tool to apply fixes.
- **Non-critical issues only:** Output the list and continue.
- **No issues at all:** Output **"Pre-Landing Review: No issues found."**
- **Check CI:** Run `gh run list --branch $(git branch --show-current) --limit 3` to show recent CI status.

### Async fallback

If running asynchronously, choose the recommended option for each critical issue.

## Rules

- Read the **FULL** diff before commenting — do not flag issues that are resolved later in the diff.
- **Read-only by default** — only use `edit` if the user explicitly chooses "Fix now."
- Be terse: one line for the problem, one line for the fix.
- Only flag real problems — skip anything that is clearly fine.
