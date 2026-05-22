#!/usr/bin/env bash
# Shared helpers for install.sh / uninstall.sh.

detect_os() {
  case "$(uname -s)" in
    Darwin) echo "mac" ;;
    Linux)  echo "linux" ;;
    *)      return 1 ;;
  esac
}

# Print one plugin name per line for every user/shared/plugins/<name>/ that
# has a .provenance.json sidecar. Empty output if none. Used by install.sh /
# uninstall.sh to surface manual /plugin install hints.
list_tracked_plugins() {
  local repo_root="$1"
  local d
  for d in "$repo_root"/user/shared/plugins/*/; do
    [ -d "$d" ] || continue
    [ -f "$d/.provenance.json" ] || continue
    basename "$d"
  done
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
