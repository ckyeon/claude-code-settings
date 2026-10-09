#!/usr/bin/env bash
# Shared helpers for install.sh, uninstall.sh, and bin/check-machine.

# Field separator for the rows list_owned_links emits. Must not be an IFS
# whitespace character, which `read` would coalesce.
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
