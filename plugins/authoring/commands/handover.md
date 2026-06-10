---
description: Draft a Claude Code handover brief for a task, in the house format
argument-hint: <task description or task id>
---

Write a **handover brief** for the following task, using the house format from
the `authoring:claude-code-handover` skill (read that skill first if it is not
already in context):

$ARGUMENTS

Requirements:

- The brief must stand alone — the implementing agent reads it cold, with no
  access to this conversation. Front-load every pointer it must read first
  (plan section, repo paths, prior PRs).
- State exactly what the task **is** and what it is **NOT** (explicit scope
  boundaries).
- Name the verify gates the agent must not guess past, and concrete acceptance
  criteria a reviewer can check against the diff alone.
- Include the standard guardrails: one PR, opened not merged; no secrets; stay
  in scope.

If the task above is too vague to write verifiable acceptance criteria, say
what is missing and ask — do not pad the brief with guesses.
