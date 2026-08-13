#!/usr/bin/env bash
# Stop hook: don't let a session in this repo end with broken cross-references.
#
# bin/adopt covers the adoption path. This covers everything else — a skill
# written by hand, a SKILL.md edited in place, a skill deleted while others
# still reference it. Those never touch adopt, and the agent that made the
# change is gone by the time CI would notice.
#
# Reads the hook payload on stdin, emits Stop-hook JSON on stdout.
# Deliberately never exits non-zero: a broken hook must not wedge the session.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
INPUT="$(cat)"

if OUTPUT="$("$REPO_ROOT/bin/check-integrity" 2>&1)"; then
  exit 0
fi

# stop_hook_active means a Stop hook already continued this turn. Blocking a
# second time risks a loop, so downgrade to a plain message and let it end.
ALREADY_BLOCKED="$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    print("1" if json.load(sys.stdin).get("stop_hook_active") else "")
except Exception:
    print("")
' 2>/dev/null)"

printf '%s' "$OUTPUT" | ALREADY="$ALREADY_BLOCKED" python3 -c '
import json, os, sys

output = sys.stdin.read().strip()

if os.environ.get("ALREADY"):
    print(json.dumps({
        "systemMessage": "bin/check-integrity is still failing; ending anyway.\n\n" + output
    }))
    sys.exit(0)

print(json.dumps({
    "decision": "block",
    "reason": (
        "bin/check-integrity failed. Resolve this before finishing:\n\n"
        + output
        + "\n\nA skill that references an uninstalled skill is inert, and stays "
        "inert through every future re-sync. Either adopt the missing dependency "
        "with bin/adopt (search the whole upstream repo — it may sit under a "
        "different category) or drop the reference. Re-run bin/check-integrity "
        "to confirm."
    ),
    "systemMessage": "Integrity check failed — Claude was asked to fix it before stopping.",
}))
'
exit 0
