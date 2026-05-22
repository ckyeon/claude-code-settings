#!/usr/bin/env bash
# Remove symlinks created by install.sh. Restore the most recent .backup-* if found.
# Only touches symlinks that point into this repo — other files are left alone.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

REPO_ROOT="$SCRIPT_DIR"
CLAUDE_DIR="$HOME/.claude"

removed=0
restored=0
skipped=0

unlink_one() {
  local target="$1"
  if [ -L "$target" ] && [[ "$(readlink "$target")" == "$REPO_ROOT/"* ]]; then
    rm "$target"
    removed=$((removed + 1))
    local latest
    latest="$(ls -1t "$target".backup-* 2>/dev/null | head -n1 || true)"
    if [ -n "$latest" ]; then
      mv "$latest" "$target"
      restored=$((restored + 1))
    fi
  else
    skipped=$((skipped + 1))
  fi
}

echo "Uninstalling Claude Code user-scope settings symlinks..."

for p in CLAUDE.md settings.json statusline-command.sh \
         skills commands agents rules output-styles \
         hooks/shared hooks/os; do
  unlink_one "$CLAUDE_DIR/$p"
done

# Remove ~/.claude/hooks/ only if it's now empty (we created it; leave alone if user added stuff)
rmdir "$CLAUDE_DIR/hooks" 2>/dev/null || true

echo "Done: $removed removed, $restored backups restored, $skipped not ours / already gone."

PLUGIN_NAMES="$(list_tracked_plugins "$REPO_ROOT")"
if [ -n "$PLUGIN_NAMES" ]; then
  echo ""
  echo "Plugin-tracked entries detected (this script does NOT remove Claude Code-installed plugins):"
  while IFS= read -r name; do
    echo "  - $name"
  done <<< "$PLUGIN_NAMES"
  echo ""
  echo "To remove them, run in a Claude Code session:"
  echo "  /plugin uninstall <name>@<marketplace>    # per plugin above"
fi

MCP_NAMES="$(list_tracked_mcp_servers "$REPO_ROOT")"
if [ -n "$MCP_NAMES" ]; then
  echo ""
  echo "MCP-tracked entries detected (this script does NOT remove registered MCP servers):"
  while IFS= read -r name; do
    echo "  - $name"
  done <<< "$MCP_NAMES"
  echo ""
  echo "To remove them, run:"
  echo "  claude mcp remove <name> -s user          # per server above"
fi
