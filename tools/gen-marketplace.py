#!/usr/bin/env python3
"""Generate `.claude-plugin/marketplace.json` from the plugins on disk.

With one skill = one plugin (plan rev2), hand-maintaining the catalog for many
plugins is untenable, so the catalog is GENERATED and committed. This script is
the catalog assembler — NOT the site generator (that lives in the private
bergner-skills-site repo). It is deliberately tiny, stdlib-only, and reads no
secrets: its only inputs are this repo's own `plugins/*/.claude-plugin/plugin.json`
manifests. (rev1 §3.1 said "no generator in the public repo"; rev2 §5 Phase B
narrows that to admit exactly this minimal catalog assembler, which keeps nothing
sensitive — see the PR.)

It reads ONLY each plugin's manifest, never any SKILL.md and never the display-only
`group:` frontmatter. That is the rev2 §3.2 decoupling enforced in code: the
grouping metadata can never enter marketplace.json nor influence a plugin
`source`/`path` (those derive solely from the plugin directory name). The flat
catalog is the only thing Claude Code consumes; the nested sidebar is built
separately by the site generator from the `group:` frontmatter.

Each plugin's `source` is the rev1/R2 `git-subdir` form (url + required `path`):
adding the catalog (over its served URL or this git repo) resolves the plugin
files from this public repo. Install grain is the plugin == one skill, so
`/plugin install <skill>@bergner-skills` installs exactly that skill.

Usage:
    python3 tools/gen-marketplace.py            # write .claude-plugin/marketplace.json
    python3 tools/gen-marketplace.py --check    # verify the committed file is in sync (CI/sanity)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO / "plugins"
CATALOG = REPO / ".claude-plugin" / "marketplace.json"

# Marketplace identity — repo-level config, the one thing not derivable from the
# plugin manifests. (Kept here, not read back from the generated catalog.)
MARKET_NAME = "bergner-skills"
MARKET_DESCRIPTION = "Herman Bergner's public marketplace of reusable Claude Code agent skills."
MARKET_OWNER = {"name": "Herman Bergner"}
REPO_GIT_URL = "https://github.com/HermanBergner/bergner-skills.git"


def build_catalog() -> dict:
    plugins = []
    for pdir in sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir()):
        manifest_path = pdir / ".claude-plugin" / "plugin.json"
        if not manifest_path.is_file():
            raise SystemExit(f"{pdir} has no .claude-plugin/plugin.json — not a plugin")
        manifest = json.loads(manifest_path.read_text("utf-8"))
        name = manifest["name"]
        if name != pdir.name:
            raise SystemExit(
                f"plugin name {name!r} != directory {pdir.name!r} in {manifest_path} "
                f"— the git-subdir path is derived from the directory, so they must match")
        plugins.append({
            "name": name,
            "source": {
                "source": "git-subdir",
                "url": REPO_GIT_URL,
                "path": f"plugins/{pdir.name}",
            },
            "description": manifest.get("description", ""),
        })
    return {
        "name": MARKET_NAME,
        "description": MARKET_DESCRIPTION,
        "owner": MARKET_OWNER,
        "plugins": plugins,
    }


def render(catalog: dict) -> str:
    return json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate the flat marketplace.json catalog.")
    ap.add_argument("--check", action="store_true",
                    help="verify the committed catalog matches the plugins (exit 1 if stale)")
    args = ap.parse_args()

    catalog = build_catalog()
    rendered = render(catalog)
    if args.check:
        current = CATALOG.read_text("utf-8") if CATALOG.is_file() else ""
        if current != rendered:
            sys.exit("marketplace.json is out of date — run: python3 tools/gen-marketplace.py")
        print("marketplace.json is in sync")
        return
    CATALOG.write_text(rendered, "utf-8")
    print(f"wrote {CATALOG.relative_to(REPO)} ({len(catalog['plugins'])} plugins)")


if __name__ == "__main__":
    main()
