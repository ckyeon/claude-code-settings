#!/usr/bin/env bash
# Shared helpers for install.sh / uninstall.sh.

detect_os() {
  case "$(uname -s)" in
    Darwin) echo "mac" ;;
    Linux)  echo "linux" ;;
    *)      return 1 ;;
  esac
}
