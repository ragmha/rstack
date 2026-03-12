# Pre-Landing Review Checklist

## Instructions

Review `git diff origin/$DEFAULT_BRANCH` for the issues listed below. For each finding, cite `file:line` and suggest a fix. Skip anything that's fine.

### Two-pass review

- **Pass 1 (CRITICAL):** blocks shipping — must be resolved before merge.
- **Pass 2 (INFORMATIONAL):** included in the PR body as non-blocking notes.

### Output format

```
Pre-Landing Review: N issues (X critical, Y informational)

**CRITICAL** (blocking):
- [file:line] Problem description
  Fix: suggested fix

**Issues** (non-blocking):
- [file:line] Problem description
  Fix: suggested fix
```

---

## Pass 1 — CRITICAL

### SQL & Data Safety (Universal)

- String interpolation/concatenation in SQL queries — use parameterized queries regardless of language/ORM.
- TOCTOU races: check-then-set that should be an atomic `WHERE … UPDATE`.
- Bypassing validation on writes (e.g., direct SQL `UPDATE` skipping model validations).
- N+1 queries: missing eager loading for associations used in loops.

### Race Conditions & Concurrency

- Read-check-write without a uniqueness constraint or retry.
- Find-or-create without a unique DB index — concurrent requests create duplicates.
- Status transitions without atomic `WHERE old = ? UPDATE SET new = ?`.
- Shared mutable state without synchronization (any language).

### Security & Trust Boundaries

- **XSS:** unescaped user input in HTML output (`innerHTML`, `dangerouslySetInnerHTML`, `|safe`, `html_safe`, `raw()`, etc.).
- **SQL injection** via string interpolation in any ORM/query builder.
- **SSRF:** user-controlled URLs passed to server-side HTTP requests without an allowlist.
- **Secret/credential exposure** in code, logs, or error messages.
- **LLM-generated values** written to DB or sent to users without validation.
- **Deserialization of untrusted data** (`pickle`, `ObjectInputStream`, `eval`, `JSON.parse` of user strings passed to `eval`).

---

## Pass 2 — INFORMATIONAL

### Python-Specific

- Django `extra()`, `raw()`, or f-string SQL without parameterization.
- Jinja2 `|safe` or `{% autoescape false %}` on user content.
- `pickle.loads()` on untrusted data.
- `async` race conditions (shared state across coroutines without locks).
- Missing `with` statement for file/connection handling.

### TypeScript/JavaScript-Specific

- Prototype pollution via `Object.assign({}, userInput)` or spread of untrusted objects.
- ReDoS: user input passed to regex with catastrophic backtracking.
- `eval()`, `Function()`, `vm.runInContext()` with user input.
- `innerHTML` or `dangerouslySetInnerHTML` with user content.
- npm supply chain: new dependencies without lockfile pinning.

### Go-Specific

- Goroutine leaks: goroutines started without cancellation context.
- `defer` in loops (defers don't run until function returns).
- Nil pointer dereference on interface types (nil interface vs nil concrete).
- `sql.Open` without `defer db.Close()`.
- Unbuffered channels causing deadlocks.

### Java/Kotlin-Specific

- `ObjectInputStream.readObject()` on untrusted data (deserialization RCE).
- JNDI injection via user-controlled lookup strings.
- Spring Expression Language injection.
- Missing `@Transactional` on multi-step DB operations.
- Mutable shared state in Spring beans (singleton scope).

### Ruby/Rails-Specific

- `html_safe`, `raw()` on user-controlled data.
- `rescue StandardError` (too broad, hides real bugs).
- `update_column`/`update_columns` bypassing validations.
- N+1 queries: missing `.includes()` for associations in loops.
- String interpolation in `where()` clauses.

### Rust-Specific

- `unsafe` blocks without safety invariant documentation.
- `.unwrap()` or `.expect()` in production code paths (use `?` or handle errors).
- `Send`/`Sync` trait violations in concurrent code.
- Missing bounds checks on slice indexing.
- Lifetime issues masked by `.clone()` (performance concern).

### Conditional Side Effects

- Code branches forgetting side effects on one path.
- Log messages claiming an action happened when it was conditionally skipped.

### Magic Numbers & String Coupling

- Bare literals used in multiple files — should be constants.
- Error strings used as query filters elsewhere.

### Dead Code & Consistency

- Variables assigned but never read.
- Comments/docstrings describing old behavior after code changed.

### Test Gaps

- Missing negative-path tests (side effects, not just status).
- Security enforcement (auth, rate limiting) without integration tests.
- Assertions on presence without format checks.

### Modern Concerns

- Dependency confusion: internal package names that could be squatted on public registries.
- LLM prompt injection: user content mixed into system prompts without sanitization.
- Supply chain: new dependencies added without security review.

---

## Gate Classification

```
CRITICAL (blocks ship):           INFORMATIONAL (in PR body):
├─ SQL & Data Safety              ├─ Language-Specific Issues
├─ Race Conditions & Concurrency  ├─ Conditional Side Effects
└─ Security & Trust Boundaries    ├─ Magic Numbers & String Coupling
                                  ├─ Dead Code & Consistency
                                  ├─ Test Gaps
                                  └─ Modern Concerns
```

---

## Suppressions — DO NOT flag

- Redundancy that aids readability.
- "Add comment explaining this constant" — constants change, comments rot.
- "Assertion could be tighter" when it already covers the behavior.
- Consistency-only suggestions.
- Regex edge cases when input is constrained.
- Anything already addressed in the diff being reviewed.
