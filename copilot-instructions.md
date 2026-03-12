# rstack Skills

This project uses [rstack](https://github.com/raghibhasan/rstack) workflow skills for GitHub Copilot. These skills use `git`, `gh` CLI, and `bash` — no MCP dependencies.

## Available Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `/plan-ceo-review` | "CEO review", "product review", "10-star" | Rethink the problem from a founder perspective. Find the 10-star product hiding inside the request. |
| `/plan-eng-review` | "eng review", "architecture review" | Lock in architecture, data flow, diagrams, edge cases, and test coverage. |
| `/review` | "review my PR", "code review" | Pre-landing review for security, race conditions, and structural issues tests miss. |
| `/ship` | "ship this", "create PR", "open PR" | Merge, test, version, changelog, push, and create PR. Fully automated. |
| `/browse` | "browse", "check the site", "test the UI" | Headless Chromium browser for web interaction, screenshots, and QA. |
| `/retro` | "retro", "weekly review" | Engineering retrospective from commit history with trend tracking. |

## Recommended Workflow

1. **Plan**: Describe what you want to build, then ask for a `/plan-ceo-review` to pressure-test the product direction
2. **Engineer**: Use `/plan-eng-review` to lock in architecture, edge cases, and test coverage
3. **Build**: Implement the plan
4. **Review**: Run `/review` to catch bugs that pass CI
5. **Ship**: Run `/ship` to merge, test, push, and open the PR
6. **Verify**: Use `/browse` to test the deployed version visually
7. **Reflect**: Run `/retro` at the end of the week

## Notes

- For web browsing and QA, always use the `/browse` skill (persistent headless Chromium, ~100ms per command)
- The `/ship` skill auto-detects your test runner, versioning system, and default branch
- The `/review` checklist covers Python, TypeScript, Go, Java, Ruby, and Rust

Inspired by [gstack](https://github.com/garrytan/gstack) by Garry Tan.
