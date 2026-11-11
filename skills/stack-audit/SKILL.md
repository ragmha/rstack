---
name: stack-audit
description: Audit installed agent skills, custom agents, and MCP servers for freshness and actual use. Use when user asks "are my skills or MCPs stale?", "why aren't these skills in use?", "audit my agent stack", or asks to review `/chronicles` usage history.
---

# Agent Stack Audit

## Inventory

List active skills, agents, MCP servers, and plugins from their real install roots and configuration. Separate host-managed tools from user-managed installs. Check quarantine records before treating an absent item as lost; never restore quarantined content.

## Verify freshness

For each installed item, identify its actual source and update mechanism. Check upstream version or content only when the source is known. Mark local projects, unpinned tools, host-managed servers, and unverifiable sources as unknown rather than guessing. Back up the specific configuration before changing it, preserve local edits, and report any required restart.

## Explain usage

Use the available session history and invocation telemetry over a bounded period. Distinguish:

- **Used** — direct invocation evidence exists.
- **No observed demand** — no relevant request appeared in the sampled history.
- **One-time setup** — expected to be quiet after initial configuration.
- **Overlap** — a specific capability is covered elsewhere; do not remove either automatically.
- **Trigger gap** — direct evidence shows a matching request did not invoke the item. Titles alone do not prove this.
- **Missing or quarantined** — the item is absent, with provenance checked before drawing conclusions.
- **Unknown** — logs do not reveal implicit loads, coverage is incomplete, or evidence is inconclusive.

Zero explicit invocations does not prove a skill is useless. Do not rank or remove items from counts alone.

## Report

Summarize what was checked, the coverage limits, evidence for each finding, updates made, and anything that needs a restart. Keep session details and private repository names out of public reports.
