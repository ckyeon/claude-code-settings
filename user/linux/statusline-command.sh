#!/usr/bin/env bash
# Status line for Claude Code on Linux.
# stdin receives session info as JSON (cwd, model, etc.) — pipe through `jq` to use it.

cat > /dev/null  # drain stdin to avoid SIGPIPE

printf "🐧 %s@%s" "$(whoami)" "$(hostname -s)"
