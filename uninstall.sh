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
