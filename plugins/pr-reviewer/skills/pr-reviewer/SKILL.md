---
name: pr-reviewer
description: >-
  Reviews a GitHub pull request for the Bergner platform — checks the diff
  against the todo task's acceptance criteria, then for scope creep, bugs,
  leaked secrets, security (OWASP), tests, and docs, surfacing only findings it
  is ≥80 confident a senior reviewer would stop the merge for. Use when working
  a todo task in the Review column, when asked to "review this PR", "review
  pull request", "check PR #N", or given a GitHub PR URL/number — especially for
  Python (FastAPI / SQLAlchemy 2.0 / uv) repos. Reads the review task for its
  repo + PR, reviews the diff read-only, and comments the verdict back on the
  task. Never approves and never merges — the human does.
group: [Review]
---

# Reviewing a pull request

This skill is how the platform reviews a pull request. It exists because the
review is wired to a specific flow — Claude Code implements a task, opens a PR,
and moves the task to **Review**; *this skill works that Review task* — and
because a useful review is high-signal, not a linter echo: it surfaces only what
a senior reviewer would actually block the merge for, and stays quiet otherwise.

Assume general knowledge of git, the `gh` CLI, PRs, OWASP, and Python — this
skill encodes only what is specific to *this* platform's review.

**Read-only and advisory.** It reviews and recommends; it never approves and
never merges — the human does. Claude never approves or merges a PR it (or
another Claude) opened. The merge is the human's gate, always.

## 0. Before you review: the context check

The todo schema and the review surface both evolve; a skill that lags them
reviews against a wrong picture. So before reviewing, confirm three things and
**flag, don't guess** if any is off:

1. **PR surface.** Prefer the `gh` CLI (the server and Claude Code have it). If
   `gh` is absent, use the `Github:` MCP tools (`Github:pull_request_read`,
   `Github:get_file_contents`, `Github:get_commit`) instead — same review, read
   path only.
2. **Todo surface.** Confirm the `todo:` tools are loaded (they load via tool
   search). You need at least `todo:get_task`, `todo:list_comments`, and
   `todo:add_comment`.
3. **The Review column's real name.** Don't assume it is literally "Review" —
   resolve the project's actual status names (`todo:list_tasks_tool` /
   the project's statuses) before filtering or reasoning about them.

If the task body references fields or tools this skill doesn't describe (schema
drift), stop and say so rather than reviewing on a stale assumption.

## 1. The flow in one breath

```
Claude Code implements a task → opens a PR → moves the task to Review
                                                      │
                                          you pick up the Review task
                                                      ▼
        find its PR → review the diff (read-only) → comment the verdict on the task
```

The task's **acceptance criteria are the contract.** The PR's whole job is to
satisfy them — no less (a criterion unmet is blocking) and no more (work beyond
them is scope creep, §5). This is the platform's "does it meet the bar" gate,
the analog of CLAUDE.md-adherence in a generic review.

## 2. Locate the task and its PR

1. Read the task: `todo:get_task`. From the body take the machine header
   **`Repo: HermanBergner/<repo>`**, the **Goal**, and the **Acceptance
   criteria** — these drive §5.
2. Find the PR. Look in the task's comments (`todo:list_comments`) and body for
   a PR URL or `#N` (Claude Code records it there when it opens the PR); a
   relation may also point to it. If you are handed a PR URL/number directly,
   use that and back-link to the task.
3. If you cannot confidently identify the PR, **stop and ask** — never review a
   guessed PR.

## 3. Skip conditions — don't review what shouldn't be reviewed

If the PR is (a) closed, (b) a draft, (c) not in need of review (an automated PR,
or trivially and obviously correct), or (d) already reviewed by you earlier —
say which, briefly, and stop. Do not proceed.

## 4. Gather context (read-only)

`gh pr view <N>`, `gh pr diff <N>`, the title/description, linked issues, and CI
status (`gh pr checks <N>`). Read the repo's root `CLAUDE.md` and any
`conventions`/`CLAUDE.md` in the directories the PR touches. **Focus the review
on the diff** — read surrounding code only to confirm or kill a specific finding,
not to hunt for unrelated issues.

## 5. Review across categories

Run these against the diff. The first two are the platform's first-class checks;
the rest are the standard reviewer pass.

1. **Acceptance criteria.** For each criterion in the task body, judge: **met /
   not met / not verifiable from the diff**. An unmet criterion is a blocking
   finding. A criterion you cannot verify is a question, not a pass.
2. **Scope.** Every changed line should trace to the task. Flag scope creep,
   drive-by refactors, and unrelated reformatting — they belong in their own PR
   (one task = one PR). This is the house discipline, enforced here.
3. **Bugs.** A shallow scan of the changed lines for real defects — logic
   errors, boundary/`None`/empty cases, missing error handling, races, resource
   leaks, API misuse. Large bugs, not nitpicks.
4. **Secrets.** Always scan the diff for committed credentials — read
   [reference/secret-scanning.md](reference/secret-scanning.md). A real leaked
   secret is always blocking.
5. **Security.** When the diff touches an auth, input, IO, query, deserialization,
   or crypto surface, read
   [reference/security-checklist.md](reference/security-checklist.md).
6. **Language-specific.** If Python files changed, read
   [reference/python-review.md](reference/python-review.md) for the platform's
   stack idioms and its do-NOT-flag list. (Add a `reference/<lang>-review.md`
   later for other languages — don't fork this skill.)
7. **Tests.** New/changed behaviour should have tests; bug fixes should have a
   regression test. Note untested behaviour change as a finding.
8. **Docs.** §9.

## 6. Confidence filter — the high-signal gate

For every candidate finding, score your confidence 0–100 that it is real and
worth raising, then **surface only findings ≥80.** If nothing clears 80, say so
and post the clean result (§8) — do not invent issues to look thorough.

| Score | Meaning |
|---|---|
| 0 | False positive under light scrutiny, or a pre-existing issue. |
| 25 | Might be real, couldn't verify; or a style point no convention calls out. |
| 50 | Verified real, but a nitpick / rare in practice / low importance. |
| 75 | Verified, very likely hit in practice, the PR's approach is insufficient — or a named convention/acceptance-criterion violation. |
| 100 | Certain; the evidence directly confirms it and it will happen in practice. |

**Do NOT flag (these are false positives here):**

- Pre-existing issues, or issues on lines the PR did not modify.
- Anything a linter/type-checker/compiler/test catches — **ruff, mypy, and
  pytest run in CI and CI is the hard merge gate.** Never echo what CI already
  blocks on (imports, type errors, formatting, style, failing tests). Add value
  *above* the linter or stay silent.
- Pedantic nitpicks a senior engineer wouldn't raise.
- General quality grumbles (coverage, "could be cleaner", broad security
  hand-waving) unless a convention or acceptance criterion names it.
- Intentional changes that are part of the task's purpose.

## 7. Severity and verdict

Order the surviving findings by severity, cite `file:line` (link with the full
commit SHA so the link renders), and give a one-line verdict.

| | Severity | Maps to |
|---|---|---|
| 🔴 | **Blocking** — leaked secret, security hole, real bug, unmet acceptance criterion | must fix before merge |
| 🟡 | **Should fix** — likely bug, missing test for changed behaviour, scope creep | fix or justify |
| 🟢 | **Nit** — minor, clearly optional | author's call |

The verdict is a recommendation to the human ("blocking issues found" /
"looks good, merge is the human's call"). **Never `gh pr review --approve`,
never `--merge`.** Note positives too — a review that only lists faults reads as
noise.

## 8. Output — comment back on the task

Comment the review summary back on the Review task with `todo:add_comment`
(append-only; you are the author). Keep it brief, no emojis in the body beyond
the severity markers, and link each finding. Do **not** move the task between
columns — the column transition (and the merge) are the human's.

Template:

```
## PR review — <repo>#<N>

**Acceptance criteria:** <n met / m total; name any unmet>
**Verdict:** <blocking issues found | no blocking issues — merge is your call>

🔴 <finding> — <file:line link>
🟡 <finding> — <file:line link>
🟢 <finding> — <file:line link>

<one line of positives, if any>
```

If nothing cleared the §6 gate:

```
## PR review — <repo>#<N>
All <n> acceptance criteria met. No blocking issues; checked bugs, secrets,
security, and scope. Merge is your call.
```

> **Posting to the GitHub PR itself is an open decision (TBD with Herman).**
> Default for now: do **not** auto-post to the PR — surface the review (the task
> comment + the chat summary) and let Herman post if he wants. When the policy is
> set, wire it here: auto-post one batched `gh pr comment` vs. draft-and-confirm.
> Either way the §7 rule holds — never approve, never merge.

## 9. Documentation review

Quick, diff-scoped: public functions/classes changed by the PR have docstrings
and the docstrings still match the new signatures; `README`/`CHANGELOG` are
updated when the change is user-facing; a new dependency is justified in the PR.
Missing docs on a user-facing change is 🟡, not 🔴.

## 10. Worked example

Review task *"Add markdown description field to projects"*, body `Repo:
HermanBergner/bergner-service-todo`, 5 acceptance criteria; a comment links
PR #142.

- `gh pr view 142` / `gh pr diff 142`; not draft/closed → proceed (§3).
- Criteria (§5.1): 4 met; the migration is **not** forward-only (it drops a
  column on downgrade) → criterion unmet → 🔴, confidence 90.
- Scope (§5.2): the PR also reformats an unrelated `router.py` import block →
  🟡 scope creep, confidence 85.
- A bare `except:` swallowing a commit error → check
  [reference/python-review.md](reference/python-review.md) → real → 🔴, 85.
- A missing type hint ruff would catch → **dropped** (§6, CI catches it).
- Comment the summary on the task (§8); leave the column and the merge to Herman.
