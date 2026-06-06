# pr-review

The platform's pull-request reviewer — it works a todo task in the **Review**
column, reviews the PR that task produced, and comments a high-signal verdict
back on the task. Read-only: it reviews and recommends, but never approves and
never merges. That stays the human's call.

## When to use it

When a Claude Code task has opened a PR and moved to Review, or any time you ask
to review a PR — "review this PR", "check PR #142", or by pasting a GitHub PR
URL. It is tuned for the platform's Python services (FastAPI, SQLAlchemy 2.0,
`uv`), but the methodology is language-agnostic.

## What you get

- The diff checked against the task's **acceptance criteria** first — the PR's
  job is to meet them, no less and no more.
- **Scope** held to one task = one PR; drive-by refactors and stray reformatting
  get flagged.
- **Secrets, security, bugs, tests, and docs** reviewed against the changed
  lines, with OWASP framing and the stack's real idioms.
- Only findings it is **≥80 confident** in — it does not echo what ruff, mypy,
  or pytest already block in CI, and it stays quiet when there is nothing to say.
- A brief, linked verdict **commented back on the Review task**, severity-ranked
  (blocking / should-fix / nit) — never an approval or a merge.
