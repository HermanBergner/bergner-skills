# claude-code-handover

The house format for handing a single, discrete task to a Claude Code agent — a brief that front-loads everything the agent must read before it starts, so it builds what you meant without improvising.

## When to use it

When you're writing a task brief or handover for an agent to implement — turning "do this" into a self-contained spec the agent can act on safely.

## What you get

- The context to read first: the plan plus pointers into the repo
- A crisp statement of what the task **is** and explicitly **is not** (scope boundaries)
- Verify gates the agent must hit and must not guess past
- Guardrails baked in: one PR opened-not-merged, no secrets, stay in scope
