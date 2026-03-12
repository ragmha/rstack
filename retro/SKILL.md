---
name: retro
description: |
  Weekly engineering retrospective. Analyzes commit history, work patterns,
  and code quality metrics with persistent history and trend tracking.
  Use when asked for a retro, retrospective, weekly review, shipping velocity,
  or engineering metrics. Trigger with /retro.
---

Generates a comprehensive engineering retrospective analyzing commit history, work patterns, and code quality metrics.

## Arguments

- `/retro` — default: last 7 days
- `/retro 24h` — last 24 hours
- `/retro 14d` — last 14 days
- `/retro 30d` — last 30 days
- `/retro compare` — compare current vs prior same-length window
- `/retro compare 14d` — compare with explicit window

## Instructions

Parse the argument for time window. Default to 7 days. Validate format: a number followed by `d`, `h`, or `w`, or the keyword `compare` with an optional window. If the format is invalid, show usage and stop.

**Auto-detect default branch:**

```bash
DEFAULT_BRANCH=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}')
DEFAULT_BRANCH=${DEFAULT_BRANCH:-main}
```

Use `origin/$DEFAULT_BRANCH` for all git queries.

### Step 1: Gather Raw Data

Run all of the following via `bash`, in parallel:

```bash
# Commits with timestamps
git log origin/$DEFAULT_BRANCH --since="<window>" --format="%H|%ai|%s" --shortstat
```

```bash
# Per-commit test vs production LOC
git log origin/$DEFAULT_BRANCH --since="<window>" --format="COMMIT:%H" --numstat
```

```bash
# Timestamps for session detection (Pacific time)
TZ=America/Los_Angeles git log origin/$DEFAULT_BRANCH --since="<window>" --format="%at|%ai|%s" | sort -n
```

```bash
# Hotspot files
git log origin/$DEFAULT_BRANCH --since="<window>" --format="" --name-only | grep -v '^$' | sort | uniq -c | sort -rn
```

```bash
# PR numbers from commit messages
git log origin/$DEFAULT_BRANCH --since="<window>" --format="%s" | grep -oE '#[0-9]+' | sort -un
```

### Step 2: Compute Metrics

Build a summary table with the following columns:

| Metric | Value |
|---|---|
| Commits | — |
| PRs merged | — |
| Insertions | — |
| Deletions | — |
| Net LOC | — |
| Test LOC | — |
| Test ratio | — |
| Version range | — |
| Active days | — |
| Detected sessions | — |
| Avg LOC/session-hour | — |

Compute each metric from the raw data gathered in Step 1. Test LOC is determined by counting insertions in files matching common test patterns (`*_test.*`, `*.test.*`, `*_spec.*`, `*.spec.*`, `test_*`, `tests/`, `__tests__/`, etc.). Test ratio = test LOC / total insertions.

### Step 3: Commit Time Distribution

Build an hourly histogram of commit times in Pacific time. Render as a bar chart using Unicode block characters. Call out:

- **Peak hours** — the 2-3 hours with the most commits
- **Dead zones** — any 4+ hour gap with zero commits
- **Bimodal patterns** — two distinct activity peaks (e.g., morning + evening)
- **Late-night clusters** — commits between midnight and 4am

### Step 4: Work Session Detection

Group commits into sessions using a **45-minute gap threshold** — any gap of 45+ minutes between consecutive commits starts a new session.

Classify each session:
- **Deep** — 50+ minutes
- **Medium** — 20–50 minutes
- **Micro** — under 20 minutes

Calculate and report:
- Total active time (sum of session durations)
- Average session length
- LOC per hour (net LOC / total active hours)

### Step 5: Commit Type Breakdown

Categorize commits by conventional commit prefix: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`, and `other` for anything that doesn't match.

Render a percentage bar chart. Flag a warning if `fix` ratio exceeds 50%.

### Step 6: Hotspot Analysis

List the **top 10 most-changed files** by number of commits touching them.

Flag:
- **Churn** — files with 5+ changes in the window
- **Test vs production ratio** — whether hot files have corresponding test files that are also active

### Step 7: PR Size Distribution

Classify PRs by total LOC changed (insertions + deletions):

| Size | LOC Range |
|---|---|
| Small | < 100 |
| Medium | 100–500 |
| Large | 500–1500 |
| XL | 1500+ |

Flag any XL PRs with their file counts and summaries.

### Step 8: Focus Score + Ship of the Week

**Focus Score** = percentage of commits in the single most-changed top-level directory. Higher is more focused.

**Ship of the Week** = the PR (or largest single commit) with the highest net LOC. Include its title and a one-line summary.

### Step 9: Week-over-Week Trends

Only include this section if the time window is **14 days or longer**.

Break the window into weekly buckets and show trends for:
- Commits per week
- LOC per week
- Test ratio per week
- Fix ratio per week
- Sessions per week

### Step 10: Streak Tracking

```bash
TZ=America/Los_Angeles git log origin/$DEFAULT_BRANCH --format="%ad" --date=format:"%Y-%m-%d" | sort -u
```

Count consecutive days with commits, walking backward from today. Report the current streak length.

### Step 11: Load History & Compare

Use `glob` to search for: `.context/retros/*.json`

- **If found:** use `view` to read the most recent file. Calculate deltas between current and previous metrics for the trends section.
- **If first run:** skip comparison and note: *"First retro — run again next week for trends."*

### Step 12: Save Retro History

```bash
mkdir -p .context/retros
```

Use the `create` tool to save a JSON snapshot to `.context/retros/${today}-${seq}.json` where `${today}` is the current date in `YYYY-MM-DD` format and `${seq}` is an incrementing number if multiple retros run on the same day.

Schema:

```json
{
  "date": "2026-03-12",
  "window": "7d",
  "metrics": {
    "commits": 47,
    "prs_merged": 12,
    "insertions": 3200,
    "deletions": 800,
    "net_loc": 2400,
    "test_loc": 1300,
    "test_ratio": 0.41,
    "active_days": 6,
    "sessions": 14,
    "deep_sessions": 5,
    "avg_session_minutes": 42,
    "loc_per_session_hour": 350,
    "feat_pct": 0.40,
    "fix_pct": 0.30,
    "peak_hour": 22
  },
  "version_range": ["1.0.0", "1.1.0"],
  "streak_days": 47,
  "tweetable": "Week of Mar 8: 47 commits, 3.2k LOC, 41% tests, 12 PRs, peak: 10pm"
}
```

### Step 13: Narrative Output

Structure the final output as follows:

1. **Tweetable summary** — one-line headline as the very first line
2. **Summary Table** — the metrics table from Step 2
3. **Trends vs Last Retro** — deltas from Step 11 (if history exists)
4. **Time & Session Patterns** — narrative interpretation of Steps 3–4
5. **Shipping Velocity** — commit type mix, PR size discipline, fix chains
6. **Code Quality Signals** — test ratio assessment, hotspot warnings, XL PR flags
7. **Focus & Highlights** — focus score, ship of the week
8. **Top 3 Wins** — best accomplishments from the window, anchored in specific commits/PRs
9. **3 Things to Improve** — specific, actionable, anchored in the data
10. **3 Habits for Next Week** — small, practical, each takes less than 5 minutes to adopt
11. **Week-over-Week** — trend tables (if window ≥ 14d)

## Compare Mode

When the user invokes `/retro compare` (with or without an explicit window):

1. Compute metrics for the **current window** (e.g., last 7 days)
2. Compute metrics for the **prior window** of the same length (e.g., 7–14 days ago)
3. Render a **side-by-side table** with deltas and directional arrows (↑/↓/→)
4. Write a narrative on improvements and regressions
5. Only save the **current-window** snapshot to `.context/retros/`

## Tone

Encouraging but candid. Be specific and concrete — skip generic praise. Reference actual commits, PRs, and files. Target **2500–3500 words**. Use markdown tables and code blocks for data, prose for narrative sections.

## Rules

- **ALL output goes to the conversation**, not to files — the only file written is the `.context/retros/` JSON snapshot
- Use `origin/$DEFAULT_BRANCH` for all git queries
- Display all times in **Pacific time**
- If zero commits are found in the window, say so clearly and suggest trying a different window
- Round LOC/hour to the nearest 50
