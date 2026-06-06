# todo MCP — tool surface reference

The exhaustive field→tool mapping for the Bergner todo MCP, the vocabularies,
and the constraints the authoring workflow depends on. SKILL.md points here;
read this before the first create in a session and to confirm the live tools
still match (the §0 drift check).

## Contents
- Provenance & drift check
- Tools by purpose (the full set)
- Field → which call sets it
- Vocabularies (status, priority, type, labels)
- Hard constraints (the gotchas)
- Bulk / atomic forms

## Provenance & drift check

Documented against the todo MCP at **alembic head 0007** (comments, labels,
task types, sub-task surfacing, vector `similar_to` all live), server prefix
**`todo`**. This is provenance, not an expiry — the live tools are
authoritative. If the live surface exposes anything not listed below (new tool,
new field on `create_task`/`update_task`, a first-class `repo`/`is_agent_task`
field), treat this reference as stale: flag it and update the skill before
relying on the old pattern.

## Tools by purpose (the full set)

Identity & discovery
- `todo:whoami` — your principal id, subject, groups (the `authz_group` values
  you may pass to create_project).
- `todo:list_projects` — projects you can see; each with id, render_mode, and
  its workflow **statuses** (id, name, category, position). Source of status ids.
- `todo:get_inbox` — your personal catch-all Inbox project.

Projects
- `todo:create_project` — `name`, `render_mode` (`board` | `list`), optional
  `authz_group` (omit = private to your personal group; a group you're in =
  shared). No description field yet (see SKILL.md §6).
- `todo:rename_project`, `todo:delete_project` (admin-gated; Inbox never
  deletable; project must be empty to delete).

Tasks — create / read / mutate
- `todo:create_task` — **`project_id`, `title`** (+ optional `body`,
  `parent_id` for a one-level sub-task, `status_id`). Bulk: `tasks=[{...}]`
  atomic, returned as a list. Does NOT take priority/type/labels/repo/is_agent_task.
- `todo:get_task`, `todo:list_tasks_tool` (filter/sort + search; see below).
- `todo:update_task` — sets **`priority`** (urgent|high|medium|low|none),
  **`due_date`**, **`assigned_to`** (a principal id who has logged in at least
  once); `clear_*` flags to null due/assignee. One id or a list (same change,
  atomic).
- `todo:set_task_status` — move a task (or list) to a status in its project.
- `todo:reorder_task` — running order within a (project, status) column via
  `before`/`after` a neighbour in the same column.
- `todo:move_task` — move a task (+ sub-tasks) to another project you belong to;
  status is re-mapped.
- `todo:delete_task` — PERMANENT; takes sub-tasks, comments, labels, relations.

Search (dedup & relation discovery — SKILL.md §5)
- `todo:list_tasks_tool(similar_to="...", include_completed=true)` — semantic
  search by meaning, scoped to your projects (never a cross-project oracle).
- `todo:list_tasks_tool(text="...", include_completed=true)` — full-text over
  title+body, same scoping. Also: `label_ids`, `type_ids`, `priorities`,
  `assigned_to_me`/`unassigned`/`assignee_id`, date ranges, `parent_id`,
  `roots_only`.

Types (controlled, per-project — the dispatch key)
- `todo:list_task_types`, `todo:create_task_type`, `todo:rename_task_type`,
  `todo:delete_task_type`.
- `todo:set_task_type` (one id or list, atomic), `todo:clear_task_type`.

Labels (free-form, per-project — descriptive grouping)
- `todo:list_labels`, `todo:create_label`, `todo:rename_label`,
  `todo:delete_label`.
- `todo:attach_label`, `todo:detach_label` (one id or list, atomic).

Comments (append-only)
- `todo:add_comment` (author is always you; you cannot attribute to another
  principal), `todo:list_comments`.

Relations (same project only)
- `todo:create_relation(source_id, target_id, type)` — `type` is one of the
  **settable** types `blocks` · `relates_to` · `duplicate_of`. `blocked_by` and
  `duplicate` are **read-only inverse views** returned when reading a task (with
  an `is_blocked` flag), never values you pass — to record "A blocked by B",
  create `blocks` from B to A.
- `todo:list_relations`, `todo:delete_relation`.

## Field → which call sets it

| Field | Set by | Notes |
|---|---|---|
| project | `create_task` (`project_id`) | placement; move via `move_task` |
| title | `create_task` | what changes; no repo/project prefix |
| body (markdown) | `create_task` (`body`) | agent 4-section / human freeform |
| status | `create_task` (`status_id`) or `set_task_status` | default = project "To do" |
| priority | `update_task` (`priority`) | urgent/high/medium/low/none; never null |
| due date | `update_task` (`due_date`) | clear via `clear_due_date` |
| assignee | `update_task` (`assigned_to`) | principal id; must have logged in once |
| type (1) | `set_task_type` | vocab must exist in the project first |
| labels (N) | `attach_label` / `detach_label` | label must exist in the project |
| parent (sub-task) | `create_task` (`parent_id`) | one level only |
| order in column | `reorder_task` | running order, distinct from priority |
| relation | `create_relation` | same project; `blocks`/`relates_to`/`duplicate_of` (`blocked_by`/`duplicate` are read-only inverses) |
| repo / is_agent_task | **body machine-header** | not a live field yet (SKILL.md §6) |

## Vocabularies

- **Status** (board default columns): To do (unstarted) · In progress (started)
  · Done (completed) · Cancelled (cancelled). Status **ids differ per project**
  — always read them from `list_projects`. Logic keys on the **category**,
  never the name.
- **Priority**: `urgent` `high` `medium` `low` `none`. Never null; set `none` to
  remove. Default new planned work to `medium` unless it clearly warrants other.
- **Type** (standard platform vocabulary, create per project): `feat` `fix`
  `chore` `refactor` `docs` `test`. One per task. The agent dispatch key.
- **Labels**: free-form, per-project, many per task. Suggested cross-cutting
  ones: `security` `hardening` `deferred` `blocked-on-smtp` `audit`
  `phase-8-gate`. Create as needed; keep names lowercase-hyphen.

## Hard constraints (the gotchas)

1. **Relations are same-project only.** Cross-project dependency → body note
   `Blocked by: <Project> / <task>`, never an edge.
2. **Types are per-project and start empty.** No global vocabulary; create the
   standard six in each project before typing tasks there.
3. **Labels and types must belong to the task's own project.** A cross-project
   label/type id reads as not-found (a deliberate no-oracle security property).
4. **Assignee must have logged in at least once** — an un-logged-in user cannot
   be assigned; unknown assignees are rejected uniformly.
5. **Sub-tasks are one level.** A sub-task cannot itself have sub-tasks.
6. **`delete_task` is permanent** and cascades to sub-tasks/comments/labels/
   relations. There is no undo.
7. **Comments are append-only**, authored as you — no edit/delete, no
   attributing to another principal.

## Bulk / atomic forms

Prefer these when authoring a project's backlog so a batch lands all-or-none:
- `create_task(tasks=[{project_id,title,body?,parent_id?,status_id?}, ...])`
  — returns the created tasks as a list; map them back to ids by title/identity
  (do not assume positional order) before group-applying attributes.
- `set_task_type(task_id=[...], type_id=...)`
- `attach_label(task_id=[...], label_id=...)`
- `update_task(task_id=[...], priority=...)`
- `set_task_status(task_id=[...], status_id=...)`
- `move_task(task_id=[...], destination_project_id=...)`
- `delete_task(task_id=[...])`

Create parents first, then sub-tasks (a sub-task needs its `parent_id`); set
type/priority/labels/relations after the rows exist. `create_relation` is the
one exception — pairwise only, so relations come last.
