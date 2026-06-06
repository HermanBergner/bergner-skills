# bergner-skills

A **Claude Code plugin marketplace** of reusable agent skills — one skill = one
plugin, installable individually. Public and free to install.

> **Starting fresh.** The marketplace has been cleared back to its machinery
> (the generated catalog, the generator, and CI). No skills are published yet;
> they are being rebuilt one at a time.

## Install

```bash
# add the marketplace once, in your shell
claude plugin marketplace add https://github.com/HermanBergner/bergner-skills.git
```

```text
# then install a skill in a Claude Code session (once any are published)
/plugin install <skill>@bergner-skills
```

## Adding a skill

1. Create `plugins/<skill>/` with a one-skill manifest
   `plugins/<skill>/.claude-plugin/plugin.json` and the skill at
   `plugins/<skill>/skills/<skill>/SKILL.md`.
2. Give the `SKILL.md` frontmatter a `description:` (the discoverable trigger)
   and a non-empty `group:` (its place in the docs-site sidebar, e.g.
   `group: [Review]`). Optionally add a repo-root `overviews/<skill>.md` for the
   docs site's "What it does" page.
3. Regenerate the catalog — **don't hand-edit it**:

   ```bash
   python3 tools/gen-marketplace.py            # rewrites .claude-plugin/marketplace.json
   python3 tools/gen-marketplace.py --check    # asserts it's in sync (CI runs this)
   ```

The catalog (`.claude-plugin/marketplace.json`) is **generated** from the plugins
on disk — one flat `git-subdir` entry per plugin — so it never drifts.

## Docs

Browsable, searchable docs for every published skill live at
**[skills.bergner.no](https://skills.bergner.no)**.
