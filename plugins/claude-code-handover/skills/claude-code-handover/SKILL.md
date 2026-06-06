---
description: The house format for handing a discrete task to a Claude Code agent. Front-loads the context the agent must read first (plan + repo pointers), states exactly what the task is and is NOT (scope boundaries), names verify gates the agent must not guess past, and lists guardrails (one PR opened-not-merged, no secrets, stay in scope). Use when writing a task brief or handover for an agent to implement, so it has what it needs and does not improvise.
group: [Authoring]
---

# Claude Code handover format

A **handover** is a self-contained brief that hands one discrete task to a Claude
Code agent which will read it cold, implement it, and open exactly one PR. The
agent does not have your conversation, your screen, or your intent — it has the
brief. A reviewer subagent later sees only the resulting diff plus the brief's
acceptance criteria. So the brief must **stand alone**: everything the agent
needs to start, to stay in bounds, and to know it is done lives in the text.

This skill is the **generic** house handover format. Its todo-resident form — the
same shape compressed into a todo task body — is [[authoring-todo-tasks]] §3a;
the two must stay consistent (same sections, same rules). Related discipline:
[[plan-format]] (the upstream plan a handover points back to) and [[pr-review]]
(the bar the resulting PR is held to).

## 1. The cold-start test

Before you send a handover, read it as the agent will: as someone who just woke
up in a fresh repo checkout with no memory of this conversation. Ask:

- Do I know **what to build** and what "done" looks like?
- Do I know **what to read first** to orient, and **where** the files are?
- Do I know **what NOT to touch**?
- Can I **verify** I succeeded without asking anyone?

If any answer is "no", the brief is not ready. A vague handover is where an agent
edits the wrong file, gold-plates, or declares victory on a half-done change.
Front-load the context; never make the agent guess silently.

## 2. The shape

A handover is a one-line machine header followed by four required sections, in
this order. This is the canonical form; [[authoring-todo-tasks]] §3a is the same
shape adapted to a todo body.

```
**Repo:** HermanBergner/<repo> · **Agent-ready:** yes

## Goal
One paragraph: what this task accomplishes and the end state.

## Context
Why it exists, what it relates to, and the background to do it cold. Point at
what to read first (§3). State cross-repo dependencies in prose — an agent
works one repo at a time.

## Affected files
- exact/path/one.py
- exact/path/two.conf
(Name real files/paths. List new files. No "the auth module".)

## Acceptance criteria
- [ ] Objectively checkable outcome, each backed by a [VERIFY] (§5)
- [ ] "All existing tests pass" / "CI green" where relevant
- [ ] Security/[audit] criteria when the work touches an authorization surface
```

Rules (identical to §3a — do not let them drift apart):
- **One task = one PR.** If you cannot describe the diff in one sentence without
  "and", split the handover.
- **3–6 acceptance criteria**, each verifiable by a human or a script — never
  "code is clean".
- **Title says what changes**, not where ("Add X", "Fix Y"); the `Repo:` line
  says where.

## 3. Read-first pointers — orient before editing

The first thing a good agent does is read, not write. Tell it exactly what:

- **The plan.** Most tasks descend from a phased plan (see [[plan-format]]); on
  this platform those live in `bergner-docs-context` under `design/phases/*.md`,
  with operational steps in `runbooks/`. Name the specific plan + section, not
  just the repo.
- **The repo.** Name the repo's own docs (README / ARCHITECTURE) and the
  surrounding code the change must match in style.
- **Ground every path in the real repo.** If you do not know the layout cold,
  read it and name actual paths. If a path genuinely cannot be confirmed yet,
  give your best path and add an explicit "confirm exact path in-repo" note —
  never leave the agent to guess. Grounding may reveal the task is already done
  or stale; if so, flag it instead of handing it off.

## 4. Scope boundary — what it IS and is NOT

Say both. The "is" is the Goal; the "is NOT" is what stops an eager agent from
wandering:

- List **non-goals** explicitly ("do not refactor X", "leave Y's formatting").
- Every changed line must trace to this brief. Adjacent cleanup, drive-by
  refactors, and speculative flexibility are out of scope — flag them, do not do
  them ([[pr-review]] enforces this on the diff).
- Match existing style even where you would do it differently.

## 5. [VERIFY] gates — checkpoints the agent must not guess past

A **[VERIFY] gate** is a named, runnable check that proves a step worked — the
difference between "I think it's done" and "the check passed". Write each
acceptance criterion so a gate can confirm it:

- App code → `[VERIFY]` the test suite (or a new test reproducing the bug)
  passes.
- Shell/infra → `[VERIFY]` `shellcheck` passes **and** a second run is a no-op
  (idempotent); config → `[VERIFY]` a clean apply reproduces the documented
  state.
- Removal/rename → `[VERIFY]` `rg <pattern>` returns zero matches.

The rule for the agent: **stop at a gate you cannot pass and surface it.** Do not
edit the test to go green, loosen the check, or proceed on a hunch past a gate. A
failed gate is information, not an obstacle to route around.

## 6. Guardrails — the non-negotiables

Restate these in every handover (or link this skill from it):

- [ ] **One PR, opened not merged.** The human reviews and squash-merges; the
  agent never merges its own PR.
- [ ] **Stay in scope** — one task per PR; surface anything else you notice
  rather than folding it in.
- [ ] **No secrets inline** — reference secrets by path/role; config is
  config-as-code (edit the repo and apply via the repo's script, never hand-edit
  a host).
- [ ] **Security criteria are first-class** — reviewed like behaviour, not bolted
  on after.
- [ ] **Record verification in the PR** — which [VERIFY] gates ran and that they
  passed.
- [ ] **Surface blockers, do not invent** — a missing decision or an unconfirmed
  path is a question back, not a guess.

## 7. Worked example

A complete handover for a small infra task (illustrative):

```
**Repo:** HermanBergner/bergner-host-config · **Agent-ready:** yes

## Goal
Add a `--keep N` flag to the Postgres backup pruner so the retention count is a
CLI argument (default unchanged) instead of a hard-coded constant.

## Context
The backup script prunes old dumps to a fixed count today; ops want to vary it
per environment without editing the script. Read first: `runbooks/backup.md` in
bergner-docs-context (the retention section) and the existing prune block in the
script. This is wiring only — no change to the backup or restore paths.

## Affected files
- backup/pg-backup.sh

## Acceptance criteria
- [ ] `--keep N` sets the retention count; omitting it preserves the current default
- [ ] invalid N (non-integer, or < 1) exits non-zero with a usage message
- [ ] [VERIFY] `shellcheck backup/pg-backup.sh` passes
- [ ] [VERIFY] a second run with the same args is a no-op (idempotent)
- [ ] no change to dump/restore behaviour; the existing cron invocation still works unchanged
```

Note the shape: a one-sentence Goal, a Context that says what to **read first**
and what is **out of scope**, exact files, and acceptance criteria each carrying
a runnable [VERIFY]. That is a handover an agent can pick up cold and a reviewer
can grade from the diff alone.
