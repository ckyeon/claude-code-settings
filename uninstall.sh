#!/usr/bin/env bash
# Remove symlinks created by install.sh. Restore the most recent .backup-* if found.
# Only touches symlinks that point into this repo — other files are left alone.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

REPO_ROOT="$SCRIPT_DIR"
CLAUDE_DIR="$HOME/.claude"

OS="$(detect_os)" || {
  echo "ERROR: Unsupported OS ($(uname -s)). Only macOS and Linux are supported." >&2
  exit 1
}

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

# The same list install.sh links from, so the two cannot drift apart.
while IFS="$FIELD_SEP" read -r _src dest; do
  unlink_one "$dest"
done < <(list_owned_links "$REPO_ROOT" "$CLAUDE_DIR" "$OS")

# Remove ~/.claude/hooks/ only if it's now empty (we created it; leave alone if user added stuff)
rmdir "$CLAUDE_DIR/hooks" 2>/dev/null || true

echo "Done: $removed removed, $restored backups restored, $skipped not ours / already gone."

PYTHONDONTWRITEBYTECODE=1 python3 "$REPO_ROOT/lib/declarations.py" uninstall-hints "$REPO_ROOT"
