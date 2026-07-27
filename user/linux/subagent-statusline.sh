#!/usr/bin/env bash
# Sub-agent status line for Claude Code.
# Receives JSON with a tasks array, outputs one JSON line per task.
#
# Parsing and serialisation both go through python3. jq is not guaranteed to be
# installed, and hand-built JSON breaks silently on a task name containing a
# quote or a backslash -- json.dumps escapes those, and the ESC in the colour
# codes, correctly.

exec python3 -c '
import json, sys, time

GREEN = "\u001b[32m"
GREY = "\u001b[90m"
RED = "\u001b[31m"
BOLD = "\u001b[1m"
RESET = "\u001b[0m"
DOT = "\u25cf"

STATUS_COLOUR = {
    "running": GREEN,
    "completed": GREY,
    "error": RED,
    "failed": RED,
}

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

now = time.time()

for task in data.get("tasks") or []:
    if not isinstance(task, dict):
        continue

    status = str(task.get("status") or "unknown")
    colour = STATUS_COLOUR.get(status, GREY)
    name = str(task.get("name") or "unnamed")

    parts = [
        colour + DOT + RESET + " " + colour + status + RESET,
        BOLD + name + RESET,
    ]

    try:
        tokens = int(task.get("tokenCount") or 0)
    except (TypeError, ValueError):
        tokens = 0
    if tokens > 0:
        shown = "%.1fk" % (tokens / 1000) if tokens >= 1000 else str(tokens)
        parts.append(GREY + shown + " tokens" + RESET)

    try:
        start = float(task.get("startTime") or 0)
    except (TypeError, ValueError):
        start = 0.0
    if start > 0:
        mins, secs = divmod(int(now - start), 60)
        human = "%dm %ds" % (mins, secs) if mins else "%ds" % secs
        parts.append(GREY + human + RESET)

    print(json.dumps(
        {"id": str(task.get("id") or ""), "content": "  ".join(parts)},
        ensure_ascii=False,
    ))
'
