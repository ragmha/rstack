# rstack

My personal stack of reusable skills, agents, and workflows for working with AI coding tools. Copy what you need, install the bundle, or follow a release-pinned link from a post.

Skills are reusable `SKILL.md` instruction files that teach an AI agent how to perform a specific workflow. Drop them into `~/.copilot/skills/` (personal) or `<repo>/.github/skills/` (project-scoped) and your agent picks them up.

Many skills here are copied or adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). See [Provenance](#provenance) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Install

```bash
copilot plugin marketplace add ragmha/rstack
copilot plugin install rstack@rstack
```

## Layout

| Path | Contents |
| --- | --- |
| `skills/<name>/SKILL.md` | Reusable agent skills; 29 included today. |
| `agents/*.agent.md` | Custom agent definitions, when added. |
| `workflows/<name>.md` | GitHub Actions / gh-aw agentic workflows, when added. |

Only `skills/` exists today. Add `"agents": "agents/"` to `plugin.json` when the first agent is added. Copy ordinary GitHub Actions YAML into your repo's `.github/workflows/`; install gh-aw workflows with `gh aw add ragmha/rstack/<name>@vX.Y.Z`.

Keep this stack generic. Project-specific canvases and experiments live in [lab](https://github.com/ragmha/lab).

## Link from a post

Pin posts to a release so their links keep pointing to the version they describe. On raghib.io:

```yaml
---
rstack:
  version: v0.2.0
  uses: [skills/diagnose]
---
```

```markdown
[diagnose](rstack:skills/diagnose)
```

The site's `rstack:` links resolve to `https://github.com/ragmha/rstack/tree/<version>/<path>`; this example targets [diagnose at v0.2.0](https://github.com/ragmha/rstack/tree/v0.2.0/skills/diagnose). Elsewhere, use that full GitHub URL directly.

## Skills

### Context & Session Management

- [`stay-sharp`](skills/stay-sharp/SKILL.md) - Apply context backpressure (silent test/build/lint wrappers, failFast, output filtering) and proactively compact before context rot hits the warm (40%) or dumb (70%) zones.
- [`handoff`](skills/handoff/SKILL.md) - Compact the current conversation into a handoff document for another agent to pick up.
- [`zoom-out`](skills/zoom-out/SKILL.md) - Tell the agent to zoom out and give a higher-level perspective on a section of code.

### Planning & Design

- [`grill-me`](skills/grill-me/SKILL.md) - Interview the user relentlessly about a plan or design until reaching shared understanding.
- [`grill-with-docs`](skills/grill-with-docs/SKILL.md) - Grill a plan against the existing domain model, sharpen terminology, and update CONTEXT.md / ADRs inline as decisions crystallise.
- [`prototype`](skills/prototype/SKILL.md) - Build a throwaway prototype to flesh out a design — a runnable terminal app for state/business-logic, or several radically different UI variations toggleable from one route.

### Issue Tracker Workflow

PRD → issues → triage → execution loop.

- [`to-prd`](skills/to-prd/SKILL.md) - Turn the current conversation into a PRD and publish it to the project issue tracker.
- [`to-issues`](skills/to-issues/SKILL.md) - Break a plan, spec, or PRD into independently-grabbable issues using tracer-bullet vertical slices.
- [`triage`](skills/triage/SKILL.md) - Triage issues through a state machine driven by triage roles — prepare them for an AFK agent or for the next person to grab.
- [`project-tracker-sync`](skills/project-tracker-sync/SKILL.md) - Keep a personal `project-tracker` repo in sync with whatever repo you're working on (kanban-style board across all your projects).

### Code Review & Architecture

- [`review`](skills/review/SKILL.md) - Review changes since a fixed point along two axes — Standards (does it follow this repo's coding standards?) and Spec (does it match what the issue/PRD asked for?). Runs both reviews in parallel sub-agents.
- [`improve-codebase-architecture`](skills/improve-codebase-architecture/SKILL.md) - Find deepening opportunities, informed by the domain language in CONTEXT.md and the decisions in `docs/adr/`.
- [`no-deprecated-code`](skills/no-deprecated-code/SKILL.md) - Zero-tolerance policy for deprecated APIs in generated or edited code: detect before writing, fix as you touch, verify before committing. Stack-agnostic with optional per-ecosystem lookup tables.
- [`refactor`](skills/refactor/SKILL.md) - Surgical code refactoring without changing behavior — extract functions, rename, break down god functions, improve type safety, eliminate code smells. Use for gradual improvements when a full rewrite would be too drastic.

### Testing

- [`tdd`](skills/tdd/SKILL.md) - Test-driven development with a strict red-green-refactor loop, vertical slices, and integration-test bias.
- [`migrate-to-shoehorn`](skills/migrate-to-shoehorn/SKILL.md) - Migrate test files from `as` type assertions to [`@total-typescript/shoehorn`](https://github.com/total-typescript/shoehorn) for safer partial test data.

### Repo Setup

- [`setup-pre-commit`](skills/setup-pre-commit/SKILL.md) - Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests.
- [`setup-skills`](skills/setup-skills/SKILL.md) - Set up an `## Agent skills` block in `AGENTS.md`/`CLAUDE.md` and `docs/agents/` so engineering skills know this repo's issue tracker, triage labels, and domain doc layout.

### Git Workflow

- [`conventional-commit`](skills/conventional-commit/SKILL.md) - Craft a Conventional Commits message for the currently staged changes — pick a type, scope, and imperative description, then commit.
- [`git-worktree`](skills/git-worktree/SKILL.md) - Isolate per-task feature work in sibling worktree directories instead of switching branches in the main checkout — protects open PRs from accidental cross-contamination.
- [`trunk-based-development`](skills/trunk-based-development/SKILL.md) - Orchestrate trunk-based development: short-lived branches off `main`, rebase (never merge) before PR, never commit directly to `main`. Delegates to `git-worktree` and `conventional-commit`.

### Debugging

- [`diagnose`](skills/diagnose/SKILL.md) - Disciplined diagnosis loop for hard bugs and performance regressions — reproduce → minimise → hypothesise → instrument → fix → regression-test.

### Cost & Billing

- [`ai-credits`](skills/ai-credits/README.md) - Track the true USD cost of agentic Copilot work and reconcile it against your plan. Ships a `cost.mjs` CLI and an optional Copilot CLI [statusline](skills/ai-credits/STATUSLINE.md).

### Writing

A three-stage pipeline: raw material → structured article → narrative beats.

- [`writing-fragments`](skills/writing-fragments/SKILL.md) - Mine yourself for fragments (claims, vignettes, sharp sentences) and append them to a single document as raw material.
- [`writing-shape`](skills/writing-shape/SKILL.md) - Take a markdown file of raw material and shape it into an article paragraph by paragraph, arguing about format at each step.
- [`writing-beats`](skills/writing-beats/SKILL.md) - Shape an article as a journey of beats, choose-your-own-adventure style — pick a starting beat, then offer options for where to pivot next.

### Skill Authoring

- [`write-a-skill`](skills/write-a-skill/SKILL.md) - Create new agent skills with proper structure, progressive disclosure, and bundled resources.

### Communication Style

- [`caveman`](skills/caveman/SKILL.md) - Ultra-compressed communication mode. Cuts token usage ~75% by dropping filler while keeping full technical accuracy.

### Wellness

- [`take-breaks`](skills/take-breaks/SKILL.md) - **Cat Gatekeeper** — a macOS launchd agent that opens a Terminal window with an animated ASCII cat and a 5-minute countdown every 30 minutes, forcing you to take a break.

## Provenance

| Origin | Skills |
|---|---|
| Upstream, [mattpocock/skills](https://github.com/mattpocock/skills) (MIT) | `grill-me`, `grill-with-docs`, `handoff`, `zoom-out`, `prototype`, `to-prd`, `to-issues`, `triage`, `review`, `improve-codebase-architecture`, `tdd`, `diagnose`, `migrate-to-shoehorn`, `setup-pre-commit`, `write-a-skill`, `caveman`, `writing-fragments`, `writing-shape`, `writing-beats` |
| Adapted from mattpocock/skills | `setup-skills` (from `setup-matt-pocock-skills`) |
| Original | `ai-credits`, `take-breaks`, `project-tracker-sync` |
| Unknown (source not yet verified) | `stay-sharp`, `git-worktree`, `trunk-based-development`, `no-deprecated-code`, `refactor`, `conventional-commit` |

## Proposed skills (not installable)

These are candidates drawn from my own projects. **None ship in the plugin yet**, and no first release has been chosen. Examples are synthetic. Proposals that come from private work are generalized and contain no private code.

| Proposal | Trigger → output | Prerequisites | Maturity | Public evidence |
|---|---|---|---|---|
| `agent-config-evals` | "eval my agent config" → deterministic pass/fail report on agent instructions/skills | Agent CLI on PATH | Proven in one repo | [chomp](https://github.com/ragmha/chomp) (`evals/`, `demo/RUNBOOK.md`) |
| `safe-local-data-mutation` | "edit my local library safely" → snapshot, transactional write, verified restore path | Local SQLite-backed app | Proven in one repo, with tests | [apple-books-mcp](https://github.com/ragmha/apple-books-mcp) |
| `copilot-canvas-extension` | "build a canvas" → scaffolded Copilot canvas extension with actions | Copilot app with canvas support | Workshop material | [build-your-copilot-canvas-extension](https://github.com/ragmha/build-your-copilot-canvas-extension) |
| `acceptance-evidence-gate` | "is this done?" → acceptance criteria mapped to evidence; blocks on gaps | Issue/spec with criteria | Generalized from private work | — |
| `tracker-migration` | "migrate Jira to Azure Boards" → readiness report, then staged, resumable migration | Source/target tracker access | Generalized from private work | — |
| `agent-telemetry` | "trace my agent session" → OTel traces/metrics for agent runs, with cost | OTel collector | Local prototype | — |

Planned extensions of existing skills (no new skill name):

- `ai-credits`: spend assessment across seats/orgs, reusing `cost.mjs`.
- `trunk-based-development`: a guided Gitflow → trunk migration, informed by [gitflow-to-trunk](https://github.com/ragmha/gitflow-to-trunk).

Deferred: native iOS UI inspection (depends on experimental simulator tooling) and incident replay (synthetic-only so far; overlaps `diagnose`). Rejected for now: a well-architected review skill whose origin and reuse rights are unclear.

Synthetic example (`acceptance-evidence-gate`):

```text
Criterion: "Export returns CSV with header row"
Evidence:  test export.spec.ts › "writes header" ✓
Criterion: "Large exports stream"
Evidence:  none → BLOCKED
```

## Installing

Verify: `copilot plugin list` and `/skills list` (should show 29 skills). Update with `copilot plugin update rstack`.

### Copilot CLI — manual copy

```bash
git clone https://github.com/ragmha/rstack.git
mkdir -p ~/.copilot/skills
cp -R rstack/skills/* ~/.copilot/skills/   # all
cp -R rstack/skills/diagnose ~/.copilot/skills/   # one
```

### Per-repo (project-scoped)

Drop a skill folder into `<repo>/.github/skills/<name>/`. Project-level skills take precedence over personal and plugin skills.

### VS Code

VS Code Copilot doesn't consume Copilot CLI plugins yet. Copy a skill into your prompts folder and reference it from chat with `#SKILL.md`:

```bash
# macOS
cp -R skills/diagnose "$HOME/Library/Application Support/Code/User/prompts/"
# Linux
cp -R skills/diagnose "$HOME/.config/Code/User/prompts/"
```

For workspace scope, copy into `<repo>/.github/prompts/` instead.

## License

[MIT](LICENSE) — © 2026 Raghib Hasan. Third-party notices: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). One PR per skill change; keep `SKILL.md` triggers sharp so model-side invocation works.
