---
name: ship
description: |
  Ship workflow. Merge default branch, run tests, review diff, bump version,
  update changelog, commit in bisectable chunks, push, and create PR. Fully
  automated — auto-detects test runner, versioning, and changelog format.
  Use when asked to ship, land a branch, push and create a PR, or open a PR.
  Trigger with /ship.
---

You are running the `/ship` workflow. This is a **non-interactive, fully automated** workflow. Do NOT ask for confirmation at any step. Run straight through and output the PR URL at the end.

## When to stop

**Only stop for:**
- On default branch (abort)
- Merge conflicts that can't be auto-resolved
- Test failures
- Pre-landing review finds CRITICAL issues and user chooses to fix
- MINOR or MAJOR version bump needed (ask)

**Never stop for:**
- Uncommitted changes (always include)
- PATCH/MICRO version bump choice (auto-pick)
- CHANGELOG content (auto-generate)
- Commit message approval
- Multi-file changesets

---

## Step 1: Pre-flight

1. **Detect default branch** using `bash`:

   ```bash
   DEFAULT_BRANCH=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}')
   DEFAULT_BRANCH=${DEFAULT_BRANCH:-main}
   ```

2. **Check current branch** via `bash`: `git branch --show-current`. If on the default branch, **abort** with a message telling the user to create a feature branch first.

3. **Run `git status`** (never use `-uall`). Uncommitted changes are always included — do not ask.

4. **Inspect the diff**:
   ```bash
   git diff $DEFAULT_BRANCH...HEAD --stat
   git log $DEFAULT_BRANCH..HEAD --oneline
   ```

---

## Step 2: Merge origin/default branch

```bash
git fetch origin $DEFAULT_BRANCH && git merge origin/$DEFAULT_BRANCH --no-edit
```

If merge conflicts arise: try to auto-resolve simple ones (VERSION files, CHANGELOG ordering conflicts). Complex conflicts → **STOP** and tell the user.

---

## Step 3: Run tests

Auto-detect the test runner by checking for project files (use `bash` to check existence):

```bash
# Detection priority order
if [ -f "package.json" ]; then
  if [ -f "bun.lock" ]; then TEST_CMD="bun test"
  elif [ -f "yarn.lock" ]; then TEST_CMD="yarn test"
  elif [ -f "pnpm-lock.yaml" ]; then TEST_CMD="pnpm test"
  else TEST_CMD="npm test"
  fi
elif [ -f "Gemfile" ]; then
  if grep -q "rspec" Gemfile; then TEST_CMD="bundle exec rspec"
  else TEST_CMD="bundle exec rake test"
  fi
elif [ -f "pyproject.toml" ] || [ -f "pytest.ini" ] || [ -f "setup.cfg" ]; then
  TEST_CMD="pytest"
elif [ -f "go.mod" ]; then
  TEST_CMD="go test ./..."
elif [ -f "Cargo.toml" ]; then
  TEST_CMD="cargo test"
elif [ -f "pom.xml" ]; then
  TEST_CMD="mvn test"
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
  TEST_CMD="gradle test"
elif [ -f "Makefile" ] && grep -q "^test:" Makefile; then
  TEST_CMD="make test"
else
  TEST_CMD=""
fi
```

- If `TEST_CMD` is empty: use `ask_user` to ask how to run tests, with an option to skip.
- If tests **fail**: show the failures and **STOP**.
- If all tests **pass**: note the counts briefly and continue.

---

## Step 4: Pre-Landing Review

1. **Load the review checklist.** Try these paths in order:
   - `.github/skills/rstack/review/checklist.md`
   - `.github/skills/review/checklist.md`
   - `~/.copilot/skills/rstack/review/checklist.md`

   If found, apply the checklist against `git diff origin/$DEFAULT_BRANCH`. If not found, do a basic structural review (obvious bugs, missing error handling, debug code left in).

2. **Two-pass classification:**
   - **CRITICAL** — blocks ship (security holes, data loss, crashes)
   - **INFORMATIONAL** — noted in PR body only

3. **CRITICAL issues:** use `ask_user` for each issue with options:
   - A) Fix now
   - B) Acknowledge and ship anyway
   - C) False positive — skip

4. If the user chose **Fix**: apply the fixes, commit them, and tell the user to run `/ship` again.

5. Save the review output for inclusion in the PR body.

---

## Step 5: Version bump (auto-decide)

**Detect versioning system** (use `bash`/`view`):

- If a `VERSION` file exists: read it, determine format (semver 3-digit `X.Y.Z` or 4-digit `X.Y.Z.W`)
- If `package.json` has a `version` field: use `npm version`
- If `pyproject.toml` has a `version` field: edit in place
- If `Cargo.toml` has a `version` field: edit in place
- If none found: **skip versioning entirely**

**Auto-decide bump level from the diff:**

- Count changed lines: `git diff origin/$DEFAULT_BRANCH --stat | tail -1`
- < 50 lines changed → **PATCH** (or MICRO if 4-digit versioning)
- 50+ lines changed → **PATCH**
- **MINOR** or **MAJOR** → use `ask_user` (only for major features or breaking changes)

Write the new version using the `edit` tool.

---

## Step 6: CHANGELOG (auto-generate, optional)

Only if `CHANGELOG.md` exists (check with `bash`):

1. Read the header to determine format via `view`.
2. Auto-generate entries from:
   ```bash
   git log $DEFAULT_BRANCH..HEAD --oneline
   git diff $DEFAULT_BRANCH...HEAD
   ```
3. Categorize changes: **Added**, **Changed**, **Fixed**, **Removed**.
4. Insert the new section after the header, dated today (YYYY-MM-DD).
5. Write changes using the `edit` tool.

---

## Step 7: Commit (bisectable chunks)

Split changes into logical, independently valid commits.

**Ordering:** infrastructure → models/services → controllers/views → VERSION + CHANGELOG

**Format:** `<type>: <summary>` where type is one of `feat`, `fix`, `chore`, `refactor`, `docs`.

Small diffs (< 50 lines, < 4 files): a single commit is fine.

---

## Step 8: Push

```bash
git push -u origin $(git branch --show-current)
```

Never force push. Regular `git push` only.

---

## Step 9: Create PR

```bash
gh pr create --title "<type>: <summary>" --body "$(cat <<'EOF'
## Summary
<bullets from CHANGELOG or diff summary>

## Pre-Landing Review
<findings from Step 4, or "No issues found.">

## Test Results
- [x] Tests pass (N tests)

Generated with GitHub Copilot
EOF
)"
```

After creating the PR, check CI status:

```bash
gh run list --branch $(git branch --show-current) --limit 1
```

**Output the PR URL as the final output.**

---

## Rules

- Never skip tests. If tests fail, stop.
- Never force push. Regular `git push` only.
- Never ask for confirmation except for MINOR/MAJOR version bumps and CRITICAL review issues.
- Date format: YYYY-MM-DD.
- Split commits for bisectability when the diff is large.
- Goal: user says `/ship`, the next thing they see is the PR URL.

## Async fallback

If running asynchronously, auto-pick recommended options and document all decisions in the PR body.
