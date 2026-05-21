#!/usr/bin/env bash
# Provenance helpers — JSON sidecar manipulation via Python 3 stdlib.
# Sourced by bin/adopt and bin/sources-index.

# Validate an adopt mode value.
validate_mode() {
  case "$1" in
    copied|inspired-by) return 0 ;;
    *) echo "ERROR: --mode must be 'copied' or 'inspired-by', got '$1'" >&2; return 1 ;;
  esac
}

# Append a provenance entry to a sidecar file (creates the file if missing,
# appends to provenance[] if it exists).
#
# Usage: append_provenance <sidecar> <source> <commit> <path> <license> <mode> <adopted_at> [notes]
append_provenance() {
  local sidecar="$1" src="$2" commit_sha="$3" src_path="$4" license="$5" mode="$6" adopted_at="$7" notes="${8:-}"

  SIDECAR_PATH="$sidecar" \
  P_SOURCE="$src" \
  P_COMMIT="$commit_sha" \
  P_PATH="$src_path" \
  P_LICENSE="$license" \
  P_MODE="$mode" \
  P_ADOPTED_AT="$adopted_at" \
  P_NOTES="$notes" \
  python3 - <<'PYEOF'
import json, os, sys

path = os.environ["SIDECAR_PATH"]
entry = {
    "source": os.environ["P_SOURCE"],
    "commit": os.environ["P_COMMIT"],
    "path": os.environ["P_PATH"],
    "license": os.environ["P_LICENSE"],
    "adopted-as": os.environ["P_MODE"],
    "adopted-at": os.environ["P_ADOPTED_AT"],
}
notes = os.environ.get("P_NOTES", "")
if notes:
    entry["notes"] = notes

if os.path.exists(path):
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, dict) or "provenance" not in data or not isinstance(data["provenance"], list):
        print(f"ERROR: malformed sidecar at {path} (missing 'provenance' list)", file=sys.stderr)
        sys.exit(1)
    data["provenance"].append(entry)
else:
    data = {"provenance": [entry]}

with open(path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
PYEOF
}
