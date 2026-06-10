# bergner-skills

A **Claude Code plugin marketplace** of reusable agent skills, grouped into
individually installable plugins. Most plugins ship a single skill; a plugin
may bundle several related skills (and slash commands). Public and free to
install.

> **Starting fresh.** The marketplace has been cleared back to its machinery
> (the generated catalog, the generator, and CI). No skills are published yet;
> they are being rebuilt one at a time.

## Install

```bash
# add the marketplace once, in your shell
claude plugin marketplace add https://github.com/HermanBergner/bergner-skills.git
```

```text
# then install a plugin in a Claude Code session (once any are published)
/plugin install <plugin>@bergner-skills
```

Installing a plugin loads every skill (and slash command) it ships. A skill is
referenced as `<plugin>:<skill>` — for a one-skill plugin that's e.g.
`pr-review:pr-review`.

## Repo layout

```
plugins/<plugin>/.claude-plugin/plugin.json   the plugin manifest (name == dir name)
plugins/<plugin>/skills/<skill>/SKILL.md      one or more skills per plugin
plugins/<plugin>/commands/<command>.md        optional slash commands
overviews/<skill>.md                          optional docs-site "What it does" page, per skill
```

The skill dir name is the skill's id and need not equal the plugin name —
though for a one-skill plugin it usually does.

## Adding a skill

**To an existing plugin** — add `plugins/<plugin>/skills/<new-skill>/SKILL.md`
(skill ids must be unique across the whole marketplace). Then do step 2 and 3
below; the catalog entry for the plugin is unchanged, so step 3 is just a
sanity check.

**As a new plugin:**

1. Create `plugins/<plugin>/` with a manifest
   `plugins/<plugin>/.claude-plugin/plugin.json` (its `name` must equal the
   directory name) and the skill at `plugins/<plugin>/skills/<skill>/SKILL.md`.
2. Give the `SKILL.md` frontmatter a `description:` (the discoverable trigger)
   and a non-empty `group:` (its place in the docs-site sidebar, e.g.
   `group: [Review]`). Optionally add a repo-root `overviews/<skill>.md` for the
   docs site's "What it does" page.
3. Regenerate the catalog — **don't hand-edit it**:

   ```bash
   python3 tools/gen-marketplace.py            # rewrites .claude-plugin/marketplace.json
   python3 tools/gen-marketplace.py --check    # asserts it's in sync (CI runs this)
   ```

A plugin may also ship slash commands as `plugins/<plugin>/commands/<name>.md`;
they install with the plugin and don't appear in the catalog (Claude Code
discovers them from the plugin dir).

The catalog (`.claude-plugin/marketplace.json`) is **generated** from the plugins
on disk — one flat `git-subdir` entry per plugin, however many skills it holds —
so it never drifts. The generator also validates every skill's frontmatter, so a
missing `description`/`group` fails CI here instead of at site-build time.

## Docs

Browsable, searchable docs for every published skill live at
**[skills.bergner.no](https://skills.bergner.no)**.
