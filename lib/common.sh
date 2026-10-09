#!/usr/bin/env bash
# Shared helpers for install.sh, uninstall.sh, and bin/check-machine.

# Field separator for the rows list_declared_plugins and list_owned_links emit. Must not be an IFS
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

# Print one "<source>|<destination>" row per owned path: the file or directory
# in this repo, and where it is symlinked under the Claude directory.
# install.sh creates these links, uninstall.sh removes them, and
# bin/check-machine verifies them, so this list is the only place that says
# which paths are owned.
list_owned_links() {
  local repo_root="$1" claude_dir="$2" os="$3" d
  echo "$repo_root/user/shared/CLAUDE.md|$claude_dir/CLAUDE.md"
  echo "$repo_root/user/shared/settings.json|$claude_dir/settings.json"
  echo "$repo_root/user/$os/statusline-command.sh|$claude_dir/statusline-command.sh"
  echo "$repo_root/user/$os/subagent-statusline.sh|$claude_dir/subagent-statusline.sh"
  for d in skills commands agents rules output-styles; do
    echo "$repo_root/user/shared/$d|$claude_dir/$d"
  done
  # Hooks: 2-tier (shared + os)
  echo "$repo_root/user/shared/hooks|$claude_dir/hooks/shared"
  echo "$repo_root/user/$os/hooks|$claude_dir/hooks/os"
}

# Print one row per declared plugin: <name>|<marketplace>|<source>|<scope>.
#
# A plugin is declared when user/shared/plugins/<name>/ exists. Its marketplace
# comes from an `enabledPlugins` key ("<name>@<marketplace>") in
# user/shared/settings.json or in a project-templates/*/.claude/settings.json.
# `source` is the marketplace's repo from `extraKnownMarketplaces`, empty for
# built-in marketplaces that need no `/plugin marketplace add`. `scope` is
# "user" or "project" where the plugin is switched on, and empty when no
# settings file enables it. Marketplace and source are empty too when no
# settings file mentions the plugin, which install.sh / uninstall.sh surface
# as a warning. The rules live in lib/declarations.py.
#
# Rows are sorted built-in marketplaces first, then third-party, then unknown —
# install.sh relies on that grouping to emit one `marketplace add` per group.
list_declared_plugins() {
  local repo_root="$1"
  PYTHONDONTWRITEBYTECODE=1 python3 - "$repo_root" <<'PY'
import os
import sys

repo_root = sys.argv[1]
sys.path.insert(0, os.path.join(repo_root, "lib"))
import declarations

entries = declarations.plugin_entries(repo_root)
sources = declarations.marketplace_sources(repo_root)

rows = []
for name in declarations.declared(repo_root, "plugins"):
    marketplace, scope = entries.get(name, ("", ""))
    rows.append((name, marketplace, sources.get(marketplace, "") if marketplace else "", scope))

# Unknown last, then third-party, then built-in.
rows.sort(key=lambda r: (2 if not r[1] else 1 if r[2] else 0, r[1], r[0]))
for row in rows:
    print("|".join(row))
PY
}

# Print one MCP server name per line for every user/shared/mcp/<name>/ that
# contains a README.md. Sidecar is optional for MCP entries (a hosted server
# without public source is declared by its README alone). Used by install.sh /
# uninstall.sh to surface manual `claude mcp add` hints.
list_declared_mcp_servers() {
  local repo_root="$1"
  local d
  for d in "$repo_root"/user/shared/mcp/*/; do
    [ -d "$d" ] || continue
    [ -f "$d/README.md" ] || continue
    basename "$d"
  done
}
