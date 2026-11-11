# Copilot instructions — rstack

A generic, reusable stack of 31 [Agent Skills](https://agentskills.io/specification) (`SKILL.md` instruction folders). Any compatible agent installs them with `npx skills add ragmha/rstack`; `mcp/server.mjs` serves the same folders over MCP with the Skills extension, plus one prompt per skill; a Copilot CLI plugin marketplace is also provided. A small Python standard-library script builds the searchable GitHub Pages catalog. Project-specific canvases belong in `ragmha/lab`, not here.

## Repository layout

```
skills/<kebab-case-name>/           # one folder per skill (the unit of change)
  SKILL.md                          # required — frontmatter + workflow
  REFERENCE.md / EXAMPLES.md / *.md # progressive disclosure (see tdd/, improve-codebase-architecture/)
  scripts/                          # optional bundled executables (.mjs, .sh, .plist)
  frames/                           # only used by take-breaks
mcp/server.mjs                      # MCP stdio server for skills/ (package.json bin)
scripts/                            # standard-library catalog builder
site/                               # static GitHub Pages catalog
plugin.json                         # Copilot CLI plugin manifest; `skills: "skills/"`
.github/plugin/marketplace.json     # `copilot plugin marketplace add` entry point
README.md                           # categorised index of every skill (must stay in sync)
CONTRIBUTING.md                     # quality bar + PR rules
```

`skills/` is the **only** skills root; the MCP server and both plugin manifests point at it. Don't introduce a parallel skills directory.

Ship workflows as Agent Skills only; harness-specific agent files are not portable. gh-aw workflows live under `workflows/<name>.md`, installable with `gh aw add ragmha/rstack/<name>@vX.Y.Z`; ordinary GitHub Actions YAML is copied into a consumer repo's `.github/workflows/`. Do not scaffold empty directories. Blog links pin to release tags, never `main`.

## How a skill is loaded (the thing that's easy to get wrong)

The agent only sees the YAML `description:` field when deciding whether to load a skill — the body of `SKILL.md` is invisible until invocation. So the description carries all the routing weight:

```yaml
---
name: skill-name                    # must match folder name
description: <what it does>. Use when <concrete trigger phrases>.
---
```

Rules (from `skills/write-a-skill/SKILL.md`):

- Frontmatter uses only Agent Skills fields (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`); put anything else under `metadata`.
- **≤ 1024 chars**, third person.
- First sentence = what it does. Second sentence = `Use when ...` with literal trigger phrases the user might say (e.g. `"diagnose this"`, `"red-green-refactor"`, `"grill me"`). Look at `diagnose`, `tdd`, `grill-me`, `caveman` for the house style.
- Aim for `SKILL.md` ≤ 100 lines. Spill detail into sibling files (`REFERENCE.md`, `EXAMPLES.md`, or topic-specific files like `tdd/mocking.md`, `improve-codebase-architecture/DEEPENING.md`) and link from `SKILL.md`. References go **one level deep**, not nested.

## Bundled scripts

Some skills ship executables under `scripts/` so the workflow runs deterministically and **costs zero AI credits** (e.g. `ai-credits/scripts/cost.mjs`, `stay-sharp/scripts/run_silent.sh`, `take-breaks/scripts/install.sh` + `com.ragmha.cat-gatekeeper.plist`). Add a script when the operation is deterministic, repeated, or needs explicit error handling — not for things the agent can reason about.

Reference bundled files relative to the skill folder (`scripts/...`, or `<skill-dir>/scripts/...` when the working directory matters), never a harness-specific install path.

## Conventions when changing skills

From `CONTRIBUTING.md` and observable patterns:

- **One PR per skill change.** Don't batch unrelated skill edits.
- **Adding a skill** requires four edits in lockstep:
  1. New folder `skills/<kebab-case-name>/SKILL.md` with valid frontmatter.
  2. Add a bullet to `README.md` under the right `###` category, in the exact format:
     ```
     - [`skill-name`](skills/skill-name/SKILL.md) - One-sentence description ending with a period.
     ```
  3. If the skill count changes, update the count in `README.md`. Keep the generic plugin and marketplace descriptions in sync.
  4. Sharpen the `description:` triggers — that's what makes invocation work.
- **New category** in README needs ≥ 2 skills before it's worth creating.
- **Don't add overlapping skills.** Extend the existing one instead.
- **Skills must be actively used**, not aspirational — the bar from CONTRIBUTING.md.

## Build / test / lint

No build step. Validate with:

- Agent Skills spec: `uvx --from "git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref" skills-ref validate skills/<name>`.
- MCP Skills extension: `npm install` then `npx -y @modelcontextprotocol/inspector --cli node mcp/server.mjs --method skills/list --verify`.
- Catalog check: `python3 scripts/build_catalog.py --check` after generating `site/catalog.json` with `python3 scripts/build_catalog.py`.
- For script-bearing skills, run the script directly (e.g. `node skills/ai-credits/scripts/cost.mjs`) before committing. Wrap test/build/lint commands with `source ~/.agents/skills/stay-sharp/scripts/run_silent.sh` then `run_silent "label" "command string"`.
- Install smoke test: `npx skills add <local-checkout-path> --list`.

## Style of the skills themselves

Skills are written as **workflows**, not single prompts — phases, checklists, anti-patterns, concrete examples. Match the voice of neighbouring skills in the same category when adding a new one (e.g. `diagnose` and `tdd` set the tone for engineering skills; `writing-fragments`/`writing-shape`/`writing-beats` set it for the writing pipeline).
