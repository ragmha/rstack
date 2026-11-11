# Contributing

Thanks for your interest! This is a personal stack of skills and workflows I use day-to-day, but improvements are welcome.

Keep contributions generic and reusable; project-specific canvases and experiments belong in [lab](https://github.com/ragmha/lab).

## Workflows

Write reusable agent workflows as Agent Skills, not harness-specific agent files. Keep gh-aw agentic workflows in `workflows/<name>.md` so people can install them with `gh aw add ragmha/rstack/<name>@vX.Y.Z`. Ordinary GitHub Actions YAML is copied into the consumer repo's `.github/workflows/`. Do not create empty directories for future content.

## Adding or improving a skill

- One pull request per skill change.
- Each skill lives in `skills/<kebab-case-name>/` with a `SKILL.md` at the root.
- Follow the [Agent Skills specification](https://agentskills.io/specification). Use only its frontmatter fields; put anything else under `metadata:`.
- The `description:` field is what the agent reads to decide when to invoke the skill — make it specific. Include trigger phrases ("Use when user says...") so model-side invocation works.
- If a skill bundles scripts, place them in a `scripts/` subdirectory and reference them relative to the skill folder, never a harness-specific install path.
- Validate before opening a PR:
  ```bash
  uvx --from "git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref" skills-ref validate skills/<name>
  npx -y @modelcontextprotocol/inspector --cli node mcp/server.mjs --method skills/list --verify
  ```
- Update `README.md` to add the skill under the right category, using the format:
  ```
  - [`skill-name`](skills/skill-name/SKILL.md) - One-sentence description ending with a period.
  ```

## Quality bar

Skills should:

- Be actively used (not aspirational).
- Have a clear `SKILL.md` describing the workflow, not just a single prompt.
- Have a sharp invocation trigger so the agent knows when to load them.
- Avoid overlap with existing skills — if there's overlap, prefer extending the existing skill.

## Adding a new category

If your skill doesn't fit an existing category in the README, propose a new one in your PR description. New categories should have at least 2 skills.
