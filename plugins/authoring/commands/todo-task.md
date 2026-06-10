---
description: Author a well-formed task in the Bergner todo MCP, in the house format
argument-hint: <what the task should get done>
---

Author a task in the Bergner todo MCP for the following, using the house
conventions from the `authoring:authoring-todo-tasks` skill (read that skill
first if it is not already in context):

$ARGUMENTS

Requirements:

- **Search first**: look for an existing task that already covers this before
  creating a duplicate; link related tasks with relations instead of repeating
  them.
- Pick the right project, type, and labels by listing what exists — don't
  guess ids.
- Write the body in the house shape (Repo / Goal / Context / Affected files /
  Acceptance) with acceptance criteria a worker can verify against.
- Use a single atomic bulk create when authoring several related tasks.

If the request is too vague for verifiable acceptance criteria, ask before
creating the task.
