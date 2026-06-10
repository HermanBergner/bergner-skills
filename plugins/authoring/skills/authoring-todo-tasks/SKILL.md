---
description: Authors well-formed tasks in the Bergner todo MCP (the `todo:` tools, e.g. todo:create_task). Use whenever work is being captured, drafted, or broken down into todo tasks for any bergner.no project — triggered by "add a task", "make tasks for X", "put this in the todo", "create a backlog", or any planning that ends in tracked work. Covers which tool sets which field, the search-first dedupe/relation step, agent vs human task bodies, the type-vs-label distinction, priorities, sub-tasks, relations, bulk authoring, and a self-check against schema drift. Consult this whenever touching the todo MCP, even if the request does not say "skill".
group: [Authoring]
---

# Authoring todo tasks

This skill is the operating manual for creating tasks in the **Bergner todo
MCP**. It exists because the todo system has a specific, non-obvious tool
surface — several fields are set by *separate* calls after create, "type" and
"label" are different things, and relations only work within one project.
Following it makes every task look and behave consistently, and makes agent
tasks executable by Claude Code without rework.

Assume general knowledge of todo apps, markdown, and PRs — this skill only
encodes what is specific to *this* MCP.

## 0. Before you author anything: the drift check

The todo schema evolves (it reached migration 0007 with comments/labels/types).
A skill that lags the schema produces broken tasks. So **before authoring**:

1. List the live todo tools available in the session (they load via tool
   search; the canonical set is in `reference/tool-surface.md`).
2. Compare to the surface documented in `reference/tool-surface.md`.
3. If the live tools expose fields or tools **not** described here (e.g. a
   first-class `repo` / `is_agent_task` field appears on `todo:create_task`, or
   a new entity), **stop and flag it** — the skill is stale and should be
   updated before relying on the old pattern. Do not silently guess.

This is a self-check, not a date stamp — the live tools are the source of truth,
this skill is the documented expectation.

## 1. The model in one breath

- **Projects** are logical domains (e.g. "Server & Infrastructure", "Todo
  Service"). Each is a **board** (workflow columns: To do / In progress / Done /
  Cancelled) or a **list** (two-state checklist). Tasks belong to a project.
- **Tasks** carry: title, body (markdown), status, priority, an optional
  **type** (one, controlled), optional **labels** (many, free-form), an
  optional **parent** (one-level sub-tasks), and **relations** to sibling tasks.
- **Authorization** is per-project via Authentik groups; you only see/act on
  projects you are a member of. Identity is a stable principal.

Full field→tool mapping and vocabularies: **`reference/tool-surface.md`** (read
it before your first create in a session).

## 2. Type vs label — do not confuse these

| | **Type** (`todo:set_task_type`) | **Label** (`todo:attach_label`) |
|---|---|---|
| Cardinality | **one** per task | **many** per task |
| Vocabulary | **controlled**, per-project | **free-form**, per-project |
| Purpose | carries *meaning*; the **agent dispatch key** the future coder reads to pick its execution profile | descriptive grouping ("tag similar tasks") |
| Examples | `feat` `fix` `chore` `refactor` `docs` `test` | `security` `hardening` `deferred` `blocked-on-smtp` |

**Type is `feat/fix/chore/...`** — it is NOT a label. Types are a per-project
controlled vocabulary and must be **created in a project before any task there
can be typed** (there is no global vocabulary). The standard vocabulary for this
platform is: **`feat` `fix` `chore` `refactor` `docs` `test`**. Create exactly
this set in each project (via `todo:create_task_type`) the first time you author
into it, then type every task.

**Choosing the type** (it is the coder dispatch key, so be consistent, not a
coin-flip):

| Type | Use when the task… |
|---|---|
| `feat` | adds new user-visible behaviour or a new capability |
| `fix` | corrects broken behaviour (a bug, a misconfiguration) |
| `chore` | is plumbing/build/tooling/config wiring — no behaviour change for users (e.g. wire a script, bump a pin, set up CI) |
| `refactor` | restructures code with behaviour deliberately preserved |
| `docs` | changes only documentation/runbooks/READMEs |
| `test` | adds or changes only tests/verification harnesses |

Tie-breakers: if it ships a new ability → `feat` even if mostly wiring; if it
only moves code around with identical behaviour → `refactor`; if a human will do
it (not Claude Code), still type it by the *nature* of the change (a DNS change
is `chore`, a decision is `chore`).

**Labels — two kinds, both fine:** an **area** label naming the domain
(`host-config`, `authentik`, `schema`, `caddy`) and a **cross-cutting** label
naming a state or theme (`security`, `hardening`, `deferred`,
`blocked-on-smtp`, `audit`). Use an area label when it helps group a repo's
work; add cross-cutting labels as they apply. Lowercase-hyphen; reuse existing
labels (`todo:list_labels`) before inventing new ones to avoid near-duplicates.

## 3. The two task profiles

Every task body is markdown and shares one feel, but branches on whether Claude
Code will execute it.

### 3a. Agent task (Claude Code will implement it)

Detailed and bounded — the body is the agent's brief, and a reviewer subagent
will see only the resulting diff plus these criteria, so the body must stand
alone. (The generic house brief format is the `claude-code-handover` skill;
this is its todo-resident form.)

**Ground it in the real repo first.** Before writing *Affected files*, if you
do not already know the repo layout cold, read it (the GitHub tools / the repo
tree) and name actual paths. If a path genuinely cannot be confirmed yet, name
your best path and add an explicit "confirm exact path in-repo" note in Context
— never leave the agent to guess silently. Vague targets ("the auth module")
are where Claude Code edits the wrong file. Grounding may also reveal the task
is **already done or stale** — if so, do NOT create it; flag it instead (the
premise was wrong).

Start with a one-line machine header (the fields the schema does not yet carry
as columns — see §6), then the four required sections **in this order**:

```
**Repo:** HermanBergner/<repo> · **Agent-ready:** yes

## Goal
One paragraph: what this task accomplishes and the end state.

## Context
Why it exists, what it relates to, and any background needed to do it cold.
State cross-project dependencies here as "Blocked by: <Project> / <task title>"
(relations cannot cross projects — see §4).

## Affected files
- exact/path/one.py
- exact/path/two.sql
(Name real files/paths. If creating new files, list them. No "the auth module".)

## Acceptance criteria
- [ ] Objectively checkable outcome (a human or test can mark it pass/fail)
- [ ] "All existing tests pass" / "CI green" where relevant
- [ ] Security/[audit] criteria when the work touches an authorization surface
```

Rules that make agent tasks executable (from Claude Code best practice):
- **One task = one PR.** If you cannot describe the diff in one sentence without
  "and", split it.
- **3–6 acceptance criteria**, each verifiable. "Code is clean" is not a
  criterion; "ruff and existing tests pass" is. For non-application work use the
  equivalent objective check for that domain: shell scripts → "shellcheck
  passes" and "a second run is a no-op" (idempotence); infra/config → "a clean
  apply reproduces the documented state"; docs → "links resolve / renders".
  The test is always: can a human or a script mark it pass/fail without
  judgement?
- **Bound the context** — exact files and current-vs-expected behaviour beat
  dumping the repo. Be extra-specific when repos/tasks have similar names.
- **Title says what changes**, not where — the project and `Repo:` say where.
  Good: `Add markdown description field to projects`. Bad:
  `bergner-service-todo: add project description`.

### 3b. Human task (the owner does it themselves)

Short, freeform markdown — a DNS change, an admin-console click, a decision.
No forced sections, no acceptance-criteria scaffold. Keep the same machine
header but `Agent-ready: no` and `Repo:` may be `n/a`.

```
**Repo:** n/a · **Agent-ready:** no

Decide whether enrollment auto-activates vs stays manual. Context: the inactive
default is a CVE-2022-23555 mitigation; weigh against one-click friction. Record
the decision in the task when made.
```

## 4. Relations — same project only

`todo:create_relation(source_id, target_id, type)` links two tasks **in the
same project** with a typed edge. The **settable** types are exactly `blocks`,
`relates_to`, and `duplicate_of`:
- `blocks` — a real ordering constraint (the source must finish before the
  target). To record "A is **blocked by** B", create a `blocks` edge **from B to
  A**. `blocked_by` is **not** a type you set — it is the read-only inverse view
  you get when reading A (with an `is_blocked` flag); likewise `duplicate` is the
  read-only inverse of `duplicate_of`.
- `relates_to` — the default for tasks in one feature. Do not overuse `blocks`;
  if two tasks can run in parallel, they are `relates_to`.
- `duplicate_of` — the source duplicates the target (rare; prefer not creating a
  duplicate at all — see §5).

**Cross-project dependencies cannot be relations.** State them in the body
Context as `Blocked by: <Project> / <task title>`. (Example: a "Coder Service"
task blocked by a "Todo Service" task is a body note, not an edge.)

You discover relation candidates by **searching first** (§5) — you cannot relate
to a task you didn't know exists.

## 5. Search before you create — dedupe & discover relations

Never author a task blind. Before creating anything, search the existing board
— it prevents duplicates, surfaces tasks the new one should relate to, and
catches work that is already done. The todo system gives you two scoped
searches (both limited to projects you can see, so they double as cross-project
relation discovery):

- **Semantic:** `todo:list_tasks_tool(similar_to="<the new task's intent in a
  sentence>", include_completed=true)` — meaning-based; the best dedup signal.
- **Full-text:** `todo:list_tasks_tool(text="<distinctive keywords>",
  include_completed=true)` — exact-term match on title+body.

Run the semantic search for every task (or, for a batch, for each distinct
piece of work); add the full-text search when there are obvious keywords. Use
`include_completed=true` so an *already-done* task is found, not just open ones.

**Then judge each strong match — do not silently proceed:**

| Match looks like… | Do |
|---|---|
| the **same** task (open or done) | **Don't create.** If done, say so. If open, stop and flag it rather than duplicate. |
| **very similar / overlapping** | **Stop and ask** the user: fold into the existing task, supersede it, or keep both? Don't auto-merge. |
| **related** (same feature/area) | Create, then `relates_to` it (same project) or note it in Context (cross-project). |
| **a dependency** (this needs that first, or blocks it) | Create, then a `blocks` edge from the blocker (same project) or a `Blocked by:` body note (cross-project). |
| **unrelated** | Proceed normally. |

This is also the only way to wire correct relations: the candidates for §4's
edges come straight out of this search. When in doubt about fold-vs-keep,
surface both to the user with a one-line diff of what each covers — the
decision is theirs.

## 6. Locked conventions (encode, don't re-ask)

- **`repo` / `is_agent_task` / `agent_ref_url` are NOT live schema fields yet.**
  Carry them in the body machine-header (`**Repo:** … · **Agent-ready:** …`)
  for now. A tracked Todo Service task will promote them to first-class fields;
  when that lands, the drift check (§0) will surface it and this skill updates
  to set them directly. The future coder reads `repo` to know what to clone and
  `is_agent_task` to know whether to pick the task up.
- **Type every task** with the standard `feat/fix/chore/refactor/docs/test`
  vocabulary (§2), creating the vocabulary per-project on first use.
- **Status** defaults to the project's "To do" column for newly planned work.
- **Sub-tasks are one level only** — a sub-task cannot have its own sub-task.

## 7. Authoring workflow (end to end)

Copy this checklist when creating tasks:

```
- [ ] 0. SEARCH first (§5): todo:list_tasks_tool(similar_to=..., include_completed=true)
        — dedupe, and collect relation candidates. Resolve fold/relate/ignore first.
- [ ] 1. Resolve the project id (todo:list_projects) and its status ids
- [ ] 2. Ensure the type vocabulary exists in the project
        (todo:list_task_types; if empty, todo:create_task_type x6)
- [ ] 3. Ensure any labels you'll use exist (todo:list_labels / create_label)
- [ ] 4. Create the task(s): todo:create_task
- [ ] 5. Set the type: todo:set_task_type
- [ ] 6. Set priority if not medium-default: todo:update_task (priority)
- [ ] 7. Attach labels: todo:attach_label
- [ ] 8. Set in-project relations: todo:create_relation
- [ ] 9. Order within a column if it matters: todo:reorder_task
```

### Bulk authoring — the default for a batch

Creating more than 2–3 tasks (a whole project's backlog) → never go one-by-one.
The order differs from the per-task checklist because relations and per-task
attributes can only be applied once the ids exist:

1. **Search still applies, per distinct item (§5).** There is no bulk search —
   run the `similar_to` (+ `text`, `include_completed=true`) search for each
   distinct piece of work *before* creating, resolve fold/relate/ignore, and
   collect relation candidates. The set you then bulk-create is already deduped.
2. **Bulk-create atomically:** `todo:create_task(tasks=[{project_id, title,
   body, status_id}, ...])` — all-or-none, returned as a list. If the batch has
   sub-tasks, create **parents first** (one bulk call), then children
   referencing `parent_id` (a second bulk call) — a sub-task needs its parent's
   id.
3. **Map the returned tasks to ids by title/identity** from the returned list
   (do not assume positional order). Then **group-apply attributes by value,
   not per task**, using the id-list forms:
   - `todo:set_task_type(task_id=[...all feat ids], type_id=<feat>)` — one call per type
   - `todo:update_task(task_id=[...all high ids], priority="high")` — one call per non-default priority
   - `todo:attach_label(task_id=[...all ids with that label], label_id=<id>)` — one call per label
4. **Wire relations after** ids exist — `todo:create_relation` is pairwise (no
   bulk form), same-project only; cross-project deps stay body notes (§4).
5. **Order** within a column only where it matters (`todo:reorder_task` takes a
   list relative to a neighbour).

Net: one bulk create + a handful of group-apply calls per project, instead of
~9 calls x N tasks. The per-task checklist still describes *what* each task
needs; this is *how* to apply it efficiently across many. Field→tool detail and
exact signatures: **`reference/tool-surface.md`**.

## 8. Language & tone

- **English** for all development specs and every agent-task body (Claude Code
  reads them as execution input).
- **Norwegian is acceptable** only inside *human*-task bodies that are personal
  or admin in nature; preserve Norwegian names/quotes verbatim, never translate
  domain terms.
- Agent tasks: imperative, precise, testable. Human tasks: brief, plain.
- Match titles to the imperative ("Add…", "Fix…", "Migrate…").

## 9. Worked example (agent task, end to end)

**Project:** Todo Service (board). **Type:** `feat`. **Priority:** high.
**Labels:** `schema`.

Title: `Add markdown description field to projects`

Body:
```
**Repo:** HermanBergner/bergner-service-todo · **Agent-ready:** yes

## Goal
Add an optional markdown `description` field to projects so each project can
carry a human-readable "what is this" blurb, set on create and editable after.

## Context
Projects currently have only name/render_mode/authz_group. The eight platform
projects need readme-style descriptions. Stored as text, rendered as markdown
by surfaces later — no rendering work in this task. Mirrors how task bodies are
treated. Forward-only migration on the todo schema (currently head 0007).

## Affected files
- todo_core/models.py
- migrations/versions/ (new forward-only revision)
- todo_core/service.py (create_project + a new update_project)
- adapters/api/router.py, adapters/schemas.py
- the MCP adapter project tools

## Acceptance criteria
- [ ] forward-only migration adds nullable `project.description` (text); existing rows unaffected
- [ ] create_project accepts optional description; a new update_project sets/clears it
- [ ] list_projects / project reads return description through both adapters (parity)
- [ ] description is plain text storage (markdown by convention); no rendering added
- [ ] all existing tests pass; CI green
```
