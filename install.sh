#!/usr/bin/env bash
# Symlink user-scope Claude Code settings from this repo into ~/.claude/.
# Idempotent: re-running is safe. Backs up existing non-symlink files before replacing.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

REPO_ROOT="$SCRIPT_DIR"
CLAUDE_DIR="$HOME/.claude"
TS="$(date +%Y%m%d-%H%M%S)"

OS="$(detect_os)" || {
  echo "ERROR: Unsupported OS ($(uname -s)). Only macOS and Linux are supported." >&2
  exit 1
}

created=0
backed_up=0
skipped=0

mkdir -p "$CLAUDE_DIR"

link_one() {
  local src="$1" dest="$2"
  if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
    skipped=$((skipped + 1))
    return
  fi
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    mv "$dest" "$dest.backup-$TS"
    backed_up=$((backed_up + 1))
  fi
  ln -s "$src" "$dest"
  created=$((created + 1))
}

echo "Installing Claude Code user-scope settings symlinks..."
echo "  REPO_ROOT:  $REPO_ROOT"
echo "  CLAUDE_DIR: $CLAUDE_DIR"
echo "  OS:         $OS"
echo ""

# Single files
link_one "$REPO_ROOT/user/shared/CLAUDE.md"          "$CLAUDE_DIR/CLAUDE.md"
link_one "$REPO_ROOT/user/shared/settings.json"      "$CLAUDE_DIR/settings.json"
link_one "$REPO_ROOT/user/$OS/statusline-command.sh" "$CLAUDE_DIR/statusline-command.sh"

# Whole directories (shared)
for d in skills commands agents rules output-styles; do
  link_one "$REPO_ROOT/user/shared/$d" "$CLAUDE_DIR/$d"
done

# Hooks: 2-tier (shared + os)
mkdir -p "$CLAUDE_DIR/hooks"
link_one "$REPO_ROOT/user/shared/hooks" "$CLAUDE_DIR/hooks/shared"
link_one "$REPO_ROOT/user/$OS/hooks"    "$CLAUDE_DIR/hooks/os"

echo ""
echo "Done: $created created, $backed_up backed up (suffix: .backup-$TS), $skipped already linked."
if [ "$backed_up" -gt 0 ]; then
  echo "Tip: review backups with: find $CLAUDE_DIR -maxdepth 2 -name '*.backup-$TS'"
fi

PLUGIN_NAMES="$(list_tracked_plugins "$REPO_ROOT")"
if [ -n "$PLUGIN_NAMES" ]; then
  echo ""
  echo "Plugin-tracked entries (NOT installed by this script — see user/shared/plugins/):"
  while IFS= read -r name; do
    echo "  - $name"
  done <<< "$PLUGIN_NAMES"
  echo ""
  echo "Inside a Claude Code session, run:"
  echo "  /plugin marketplace add <source-url>      # if not yet registered"
  echo "  /plugin install <name>@<marketplace>      # per plugin above"
fi

MCP_NAMES="$(list_tracked_mcp_servers "$REPO_ROOT")"
if [ -n "$MCP_NAMES" ]; then
  echo ""
  echo "MCP-tracked entries (NOT registered by this script — see user/shared/mcp/):"
  while IFS= read -r name; do
    echo "  - $name"
  done <<< "$MCP_NAMES"
  echo ""
  echo "For each, open user/shared/mcp/<name>/README.md and run the registration"
  echo "command shown there (typically: claude mcp add --scope user ...)."
fi
