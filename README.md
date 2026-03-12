# rstack

Six specialist modes for GitHub Copilot. Plan → Review → Ship → Verify.

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ /plan-ceo-review│  │ /plan-eng-review│  │    /review      │
│   🎯 Founder    │  │   🏗️  Engineer   │  │  🔍 Reviewer    │
│                 │  │                 │  │                 │
│ "Is this the    │  │ Architecture,   │  │ Security, races,│
│  right product?"│  │ edge cases,     │  │ trust boundaries│
│                 │  │ test plan       │  │ (multi-stack)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│     /ship       │  │    /browse      │  │     /retro      │
│  🚀 Shipper     │  │   👁️  QA        │  │  📊 Analyst     │
│                 │  │                 │  │                 │
│ Test, version,  │  │ Headless Chrome │  │ Commits, velocity│
│ push, open PR   │  │ click, screenshot│ │ streaks, trends │
│ (auto-detects)  │  │ verify, 40+ cmds│  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Quick Start

### Copilot CLI

```bash
git clone https://github.com/ragmha/rstack.git ~/.copilot/skills/rstack
cd ~/.copilot/skills/rstack && ./setup
```

### VS Code

```bash
git clone https://github.com/ragmha/rstack.git .github/skills/rstack
rm -rf .github/skills/rstack/.git
cd .github/skills/rstack && ./setup
cp .github/skills/rstack/copilot-instructions.md .github/copilot-instructions.md
```

### Verify

Type `/plan-ceo-review` in Copilot. If skills don't appear, run `./setup` again.

> **Requires:** Git, [gh CLI](https://cli.github.com/). [Bun](https://bun.sh/) only for `/browse`.
>
> **Works with:** Copilot CLI ✅ · VS Code agent mode ✅ · Coding agent ⚠️ (no interactive questions)

## Skills

### `/plan-ceo-review` — Shape the product

```
You:     "I want to add photo upload for sellers"

Copilot: "Photo upload is not the feature. The real job is helping sellers
          create listings that sell. 10-star version: auto-identify the
          product, pull specs, draft the listing, suggest the best image."
```

Three modes: **Expand** · **Hold** · **Reduce**

### `/plan-eng-review` — Lock in architecture

```
You:     "Eng review this plan"

Copilot: ┌─────────┐    ┌──────────┐    ┌───────────┐
          │ Upload  │───▶│ Classify │───▶│ Enrich    │
          └─────────┘    └──────────┘    └───────────┘

          "What if classification is low-confidence?
           Missing: orphan cleanup for failed uploads.
           Test plan: 12 scenarios."
```

Four sections: Architecture → Code Quality → Tests → Performance

### `/review` — Catch what CI misses

```
You:     "/review"

Copilot: Pre-Landing Review: 2 issues (1 critical)

         CRITICAL:
         ⚠️  src/api.py:42 — SQL injection via string interpolation
            Fix: Use parameterized query

         📝 src/utils.ts:18 — Prototype pollution via Object.assign
```

Checks: Python · TypeScript · Go · Java · Ruby · Rust

### `/ship` — One command to land

```
You:     "/ship"

Copilot: ✓ Detected pyproject.toml → pytest
         ✓ 47 tests passed
         ✓ Version: 1.4.2 → 1.4.3
         ✓ PR #42 opened
```

Auto-detects: npm · pytest · go test · cargo test · rspec · maven · make

### `/browse` — Give Copilot eyes

```
You:     "/browse staging.myapp.com — test the signup flow"

Copilot: > goto /signup
         > fill @e2 "test@example.com"
         > click @e5 "Submit"
         > screenshot /tmp/signup.png
         ✅ Signup works. No console errors.
```

Persistent headless Chromium. 40+ commands. ~100ms per call.

### `/retro` — Data, not vibes

```
You:     "/retro"

Copilot: Week of Mar 8: 32 commits, 2.1k LOC, 41% tests | Streak: 12d
         Ship of the week: Billing integration (650 LOC)
         To improve: test ratio dropped — add webhook tests
```

Saves JSON history for week-over-week trend comparison.

## Supported Stacks

| File | Tests | Review Checks |
|------|-------|---------------|
| `package.json` | npm/yarn/bun test | Prototype pollution, ReDoS, innerHTML |
| `pyproject.toml` | pytest | Django raw SQL, pickle, async races |
| `go.mod` | go test ./... | Goroutine leaks, defer misuse, nil interfaces |
| `Cargo.toml` | cargo test | Unsafe blocks, unwrap in prod, Send/Sync |
| `Gemfile` | rspec/rake | html_safe, N+1, rescue StandardError |
| `pom.xml` | mvn test | Deserialization, JNDI, Spring injection |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Skill not found | `cd ~/.copilot/skills/rstack && ./setup` |
| `/browse` binary missing | `bun install && bun run build` in rstack dir |
| Bun not installed | `curl -fsSL https://bun.sh/install | bash` |
| `gh` not installed | [cli.github.com](https://cli.github.com/) |

**Upgrade:** `cd ~/.copilot/skills/rstack && git pull && ./setup`

**Uninstall:** `rm -rf ~/.copilot/skills/rstack`

## License

MIT — Inspired by [gstack](https://github.com/garrytan/gstack) by [Garry Tan](https://x.com/garrytan).
