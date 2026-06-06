# Python review (the platform's stack)

Read this when a PR changes Python files. It encodes what is specific to *this*
platform — the linter config (so you don't duplicate it), the framework idioms
that look wrong but aren't, and the security classes worth a real look. General
Python knowledge is assumed.

## Contents

- The stack and the CI gate
- Do NOT flag (idioms + what CI already catches)
- Real findings worth flagging
- Security classes (bandit-style), mapped to this stack

## The stack and the CI gate

The platform's Python services (e.g. `bergner-service-todo`) are: Python ≥3.12,
FastAPI, SQLAlchemy 2.0, Alembic, psycopg, FastMCP, built with `uv` + hatchling,
tested with pytest. Lint/format is **ruff**, configured as:

- `line-length = 88`, `target-version = "py312"`
- `select = ["E", "W", "F", "I", "B", "UP"]`
- `extend-immutable-calls = ["fastapi.Depends", "fastapi.Query"]`

**CI is the hard merge gate** and runs `uv sync --frozen` → `ruff check .` →
`pytest -q`. Anything in that gate is already enforced — see the do-not-flag
list below.

## Do NOT flag

**Because CI already blocks on it** (don't echo the linter):

- Import ordering/unused imports, `E`/`W`/`F` style, line length — `ruff`.
- Missing/incorrect type hints in the narrow sense ruff's selected rules catch,
  formatting, trailing newlines.
- `pyupgrade` (`UP`) modernizations — ruff rewrites these.
- A failing/forgotten test — pytest fails CI; don't also "review" it.

**Because they are intended framework idioms here, not bugs:**

- `def handler(x = Depends(get_thing))` / `q: str = Query(...)` — function-call
  defaults in FastAPI argument lists. Ruff's `B008` is suppressed for exactly
  these via `extend-immutable-calls`; flagging them is a false positive.
- SQLAlchemy 2.0 style: `Mapped[...]` / `mapped_column(...)`, `select(...)` with
  `session.execute(...).scalars()`, `DeclarativeBase`. This is correct modern
  usage — don't suggest 1.x `Query`/`Column` patterns.
- Pydantic v2: `model_config`, `model_validate`, `field_validator` — not the v1
  `Config`/`validator` spellings.
- FastMCP / async handlers using `async def` with `await` on the DB session.

## Real findings worth flagging

Diff-scoped, score ≥80 only (SKILL.md §6):

- **Bare `except:` or `except Exception:` that swallows the error** — especially
  around a DB commit, a network call, or a transaction boundary. Silent failure
  is a real bug.
- **Sync blocking call inside an `async def`** (blocking IO, `time.sleep`, a sync
  driver) — stalls the event loop.
- **Session/transaction misuse** — a commit that can't roll back on error, a
  session shared across requests/tasks, a missing `await` on an async call.
- **Mutable default argument** (`def f(x=[])`) — `B006`; ruff flags it, but call
  it out if it slips a noqa.
- **`None`/empty/boundary** cases the diff introduces and doesn't handle.
- **Alembic migration that is not forward-only / not reversible as the task
  requires**, or that will lock a large table — schema changes are high-blast.
- **Behaviour change with no test**, or a bug fix with no regression test.

## Security classes (bandit-style), mapped to this stack

Look harder when the diff touches these. (`bandit` may not be installed at
review time — reason from the diff and recommend a `bandit`/`semgrep` run for an
authoritative pass; see also reference/security-checklist.md.)

- `eval` / `exec` / `compile` on anything request-derived.
- `subprocess(..., shell=True)` or shell string interpolation (`B602`/`B605`).
- `yaml.load` without `SafeLoader`; `pickle`/`marshal` of untrusted data.
- Raw SQL built by string concatenation/f-string instead of bound parameters —
  with SQLAlchemy 2.0 use `text()` + bind params or the Core/ORM constructs.
- Weak crypto (`md5`/`sha1`/DES) for a security purpose; `random` (not
  `secrets`) for tokens/passwords.
- FastAPI/JWT: algorithm not pinned (`alg` accepting `none`/unspecified),
  auth/permission check missing on a route that mutates, secrets read from the
  environment and then logged.
- `DEBUG`/verbose error pages on; binding `0.0.0.0` in a context that shouldn't.
- `assert` used for a security/authorization check (stripped under `-O`).
