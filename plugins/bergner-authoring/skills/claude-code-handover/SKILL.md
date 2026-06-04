---
description: The house format for handing a discrete task to a Claude Code agent. Front-loads the context the agent must read first (plan + repo pointers), states exactly what the task is and is NOT (scope boundaries), names verify gates the agent must not guess past, and lists guardrails (one PR opened-not-merged, no secrets, stay in scope). Use when writing a task brief or handover for an agent to implement, so it has what it needs and does not improvise.
---

# Claude Code handover format

> **Stub — Task 1 of the skills-marketplace plan.** The `description` in the
> frontmatter above is the real, discoverable trigger and is meant to be
> accurate now. This body is a deliberate placeholder: the full skill content
> lands in **Task 5**, captured from the platform's actual handover artefacts.
>
> See `design/phases/skills-marketplace-plan.md` (§8, "stub-first content") in
> `bergner-docs-context`. Related: [[plan-format]], [[pr-review]].

<!-- TODO(task-5): document the handover format — the read-first pointers, the
     scope boundary, the [VERIFY] gate pattern, and the guardrail checklist,
     with a worked example. -->
