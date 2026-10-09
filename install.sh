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

# Owned paths. The list lives in lib/common.sh so bin/check-machine verifies
# exactly what this script links.
mkdir -p "$CLAUDE_DIR/hooks"
while IFS="$FIELD_SEP" read -r src dest; do
  link_one "$src" "$dest"
done < <(list_owned_links "$REPO_ROOT" "$CLAUDE_DIR" "$OS")

echo ""
echo "Done: $created created, $backed_up backed up (suffix: .backup-$TS), $skipped already linked."
if [ "$backed_up" -gt 0 ]; then
  echo "Tip: review backups with: find $CLAUDE_DIR -maxdepth 2 -name '*.backup-$TS'"
fi

# What to run for each declared plugin and MCP server. lib/declarations.py
# words it, so the same rules decide what is declared here and in the checks.
PYTHONDONTWRITEBYTECODE=1 python3 "$REPO_ROOT/lib/declarations.py" install-hints "$REPO_ROOT"

echo ""
echo "Secrets are entered by hand: see docs/SECRETS.md."
echo "When all of the above is done, run bin/check-machine. No errors means this"
echo "machine matches what the repo owns and declares."
