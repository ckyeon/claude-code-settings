#!/usr/bin/env python3
"""SessionStart hook: report how many suggestions wait in inbox/ (ADR 0098).

Sessions in other projects write them through bin/suggest-setting. The user
sees the count, and Claude is told where the procedure is. Silent when the
inbox is empty, and never fails the session start.
"""

import json
import sys
from pathlib import Path

INBOX = Path(__file__).resolve().parent.parent.parent / "inbox"


def main() -> None:
    try:
        count = len(list(INBOX.glob("*.md")))
    except OSError:
        return
    if not count:
        return
    json.dump({
        "systemMessage": "설정 건의 %d건이 inbox/에 있습니다." % count,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "inbox/에 처리하지 않은 건의가 %d건 있다. 사용자가 처리를 요청하면 CLAUDE.md의 "
                                 "\"Process suggestions\" 절차를 따른다." % count,
        },
    }, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
