#!/usr/bin/env bash
# Shared helpers for install.sh / uninstall.sh.

# Field separator for the rows list_tracked_plugins emits. Must not be an IFS
# whitespace character: `read` coalesces runs of those, which would swallow the
# empty `source` field of a built-in marketplace and shift every later field.
FIELD_SEP="|"

detect_os() {
  case "$(uname -s)" in
    Darwin) echo "mac" ;;
    Linux)  echo "linux" ;;
    *)      return 1 ;;
  esac
}

# Print one row per tracked plugin: <name>|<marketplace>|<source>|<scope>.
#
# A plugin is tracked when user/shared/plugins/<name>/ has a .provenance.json
# sidecar. Its marketplace comes from the `enabledPlugins` key ("<name>@<marketplace>")
# in user/shared/settings.json, or — for project-scope plugins — in a
# project-templates/*/.claude/settings.json. `source` is the marketplace's repo
# from `extraKnownMarketplaces`, empty for built-in marketplaces that need no
# `/plugin marketplace add`. Both are empty when no settings file enables the
# plugin, which install.sh / uninstall.sh surface as a warning.
#
# Rows are sorted built-in marketplaces first, then third-party, then unknown —
# install.sh relies on that grouping to emit one `marketplace add` per group.
list_tracked_plugins() {
  local repo_root="$1"
  python3 - "$repo_root" <<'PY'
import glob
import json
import os
import sys

repo_root = sys.argv[1]


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


plugins_dir = os.path.join(repo_root, "user", "shared", "plugins")
try:
    tracked = sorted(
        name
        for name in os.listdir(plugins_dir)
        if os.path.isfile(os.path.join(plugins_dir, name, ".provenance.json"))
    )
except OSError:
    tracked = []

user_settings = load(os.path.join(repo_root, "user", "shared", "settings.json"))

# User scope wins: a plugin enabled globally is installed regardless of template.
enabled = {}
for scope, settings in [("user", user_settings)] + [
    ("project", load(p))
    for p in sorted(glob.glob(os.path.join(repo_root, "project-templates", "*", ".claude", "settings.json")))
]:
    for key in settings.get("enabledPlugins", {}):
        name, _, marketplace = key.partition("@")
        enabled.setdefault(name, (marketplace, scope))

marketplaces = user_settings.get("extraKnownMarketplaces", {})


def source_of(marketplace):
    source = marketplaces.get(marketplace, {}).get("source", {})
    return source.get("repo") or source.get("url") or ""


rows = []
for name in tracked:
    marketplace, scope = enabled.get(name, ("", ""))
    rows.append((name, marketplace, source_of(marketplace) if marketplace else "", scope))

# Unknown last, then third-party, then built-in.
rows.sort(key=lambda r: (2 if not r[1] else 1 if r[2] else 0, r[1], r[0]))
for row in rows:
    print("|".join(row))
PY
}

# Print one MCP server name per line for every user/shared/mcp/<name>/ that
# contains a README.md. Sidecar is optional for MCP entries (hosted servers
# without public source still get tracked via README alone). Used by install.sh /
# uninstall.sh to surface manual `claude mcp add` hints.
list_tracked_mcp_servers() {
  local repo_root="$1"
  local d
  for d in "$repo_root"/user/shared/mcp/*/; do
    [ -d "$d" ] || continue
    [ -f "$d/README.md" ] || continue
    basename "$d"
  done
}
