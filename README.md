# bergner-skills

A **Claude Code plugin marketplace** of reusable agent skills — house formats
and disciplines for writing plans, Claude Code task handovers, PR reviews, and
repo docs. Public and free to install.

## Install

```bash
# 1. add the marketplace (run once, in your shell)
claude plugin marketplace add https://skills.bergner.no/marketplace
```

```text
# 2. install the plugin (in a Claude Code session) — installs all its skills
/plugin install bergner-authoring@bergner-skills
```

Once installed, the skills auto-trigger by description; Claude references them as
`bergner-authoring:<skill>` (e.g. `bergner-authoring:plan-format`). You rarely
type that — installing the plugin is the only step.

## What's inside

One plugin, `bergner-authoring`, with four skills:

| Skill | What it is |
| --- | --- |
| `plan-format` | the house format for a phased implementation/design plan |
| `claude-code-handover` | the house format for handing a discrete task to a Claude Code agent |
| `pr-review` | the house pull-request discipline (one task = one PR, opened not merged) |
| `repo-doc-standard` | the standard for how a repo documents itself (README vs architecture vs runbooks) |

## Docs

Browsable, searchable docs for every skill live at
**[skills.bergner.no](https://skills.bergner.no)**.
