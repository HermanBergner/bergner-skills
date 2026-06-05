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
# 2. install just the skill(s) you want (in a Claude Code session)
/plugin install plan-format@bergner-skills
```

**One skill = one plugin** (plan rev2), so each `/plugin install
<skill>@bergner-skills` installs exactly that one skill — nothing else. Install
as few or as many as you like. (The old `bergner-authoring` bundle that
installed all four at once is retired; install per-skill instead.)

Once installed, a skill auto-triggers by its description; Claude references it as
`<skill>:<skill>` (e.g. `plan-format:plan-format`) — you rarely type that.

## What's inside

Four one-skill plugins (each installs independently):

| Plugin / skill | What it is |
| --- | --- |
| `plan-format` | the house format for a phased implementation/design plan |
| `claude-code-handover` | the house format for handing a discrete task to a Claude Code agent |
| `pr-review` | the house pull-request discipline (one task = one PR, opened not merged) |
| `repo-doc-standard` | the standard for how a repo documents itself (README vs architecture vs runbooks) |

On the [docs site](https://skills.bergner.no) these are grouped under an
**Authoring** folder — a display-only taxonomy declared by each skill's
`group:` frontmatter, independent of how you install it.

## Adding a skill

1. Create `plugins/<skill>/` with a one-skill manifest
   `plugins/<skill>/.claude-plugin/plugin.json` and the skill at
   `plugins/<skill>/skills/<skill>/SKILL.md`.
2. Give the `SKILL.md` frontmatter a `description:` (the discoverable trigger)
   and a non-empty `group:` (an array of folder segments — its place in the
   docs-site sidebar, e.g. `group: [Authoring]` or `group: [Fabric, "Power BI"]`).
3. Regenerate the catalog — **don't hand-edit it**:

   ```bash
   python3 tools/gen-marketplace.py            # rewrites .claude-plugin/marketplace.json
   python3 tools/gen-marketplace.py --check    # asserts it's in sync
   claude plugin validate .                     # marketplace + manifests pass
   ```

The catalog (`.claude-plugin/marketplace.json`) is **generated** from the
plugins on disk — one flat `git-subdir` entry per plugin — so it never drifts.
`tools/gen-marketplace.py` reads only the plugin manifests, never the `group:`
frontmatter: the flat install catalog and the nested display tree stay decoupled.

## Docs

Browsable, searchable docs for every skill live at
**[skills.bergner.no](https://skills.bergner.no)**.
