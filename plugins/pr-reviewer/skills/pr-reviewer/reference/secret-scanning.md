# Secret scanning (the diff)

Read this for every review (SKILL.md §5.4). A committed credential is always a
🔴 blocking finding — and, once pushed, must be treated as compromised and
rotated, not just deleted. This file is what to look for in the diff and which
tools to lean on.

## Contents

- What to scan
- Patterns and key prefixes
- Tools (scanner MCP, gitleaks, trufflehog)
- If you find one

## What to scan

The added/changed lines of the diff, plus any new or modified `.env`,
config, notebook (`.ipynb` output cells leak constantly), fixture, or test
file. High-entropy string literals assigned to a name like `key`, `token`,
`secret`, `password`, `pat`, `apikey`, or passed to an auth call.

A value that is obviously a placeholder (`xxxx`, `<your-token>`, `changeme`,
`example`) is not a finding. A real-looking high-entropy value is.

## Patterns and key prefixes

Recognisable prefixes (non-exhaustive): `sk-` / `sk_live_` (OpenAI/Stripe-style),
`AKIA…` (AWS access key id), `ghp_` / `gho_` / `github_pat_` (GitHub tokens),
`xoxb-` / `xoxp-` (Slack), `glpat-` (GitLab), `-----BEGIN … PRIVATE KEY-----`
(PEM keys), `eyJ…` (a JWT — judge whether it's a real signing secret vs. a
sample). Connection strings with an inline password (`postgres://user:pass@…`).

Heuristic for the rest: a long (≥20 char) mixed-case+digits (+symbol) literal
with no obvious non-secret purpose, especially near an auth/config name.

## Tools

- **`Github:run_secret_scanning`** (MCP) — pass the raw diff hunks or file
  contents (not paths) to scan changed content directly. Use it as the first
  pass when reviewing through the GitHub MCP tools.
- **`gitleaks`** — fast regex+entropy scanner; the right local/pre-commit tool.
- **`trufflehog`** — broad detector set with *active verification* (it can test
  whether a found credential is live), which cuts false positives sharply.

The review runtime may not have `gitleaks`/`trufflehog` installed — reason from
the diff using the patterns above and **recommend** an authoritative scan rather
than claiming you ran one. GitHub's native push-protection covers partner
patterns only, so it is a backstop, not a substitute.

## If you find one

- 🔴 blocking, high confidence — name the file and line, do **not** reproduce the
  secret value in your comment (link the line instead).
- State plainly that the credential must be **rotated/revoked** (git history
  keeps it even after the line is deleted) and moved to OpenBao, and the file
  removed from the diff.
