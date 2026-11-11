---
name: repo-status
description: Read-only summary of repository state, recent work, and blockers. Use when the user asks "what's the state of this project?", "project status check", or "is this repo healthy?"
---

# Repository status

Give a concise, evidence-based snapshot of the current repository:

- Current branch and working-tree state.
- Recent commits and any linked issue or pull request.
- Relevant CI/check status when available.
- Known blockers or missing evidence.

Use read-only GitHub and Git commands. Do not edit files, run fixers, stage, commit, push, create issues or pull requests, or change settings. Do not expose secrets or infer status from a branch name; say when a source is unavailable.
