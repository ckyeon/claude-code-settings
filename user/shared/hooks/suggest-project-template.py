#!/usr/bin/env python3
"""새 프로젝트에서 세션이 시작되면 template 적용을 제안하라고 Claude에게 알린다 (ADR 0097).

SessionStart hook이다. stdin으로 받은 JSON의 `source`와 `cwd`를 보고, 새 프로젝트로 보일 때만
`additionalContext`에 안내를 남긴다. 안내는 사용자에게 보이지 않고, 실제 절차는
`apply-project-template` skill에 있다.

새 프로젝트로 보는 조건. 모두 맞아야 한다.
  - `source`가 `startup`이다.
  - `cwd`가 home 디렉터리가 아니고, 임시 디렉터리(`$TMPDIR`, `/tmp`) 아래도 아니다. eval 작업 디렉터리가 여기서 빠진다.
  - `cwd`에 `CLAUDE.md`도 `.claude/settings.json`도 없다.
  - git repo가 아니거나 commit이 1개 이하다.
  - `.git`, `node_modules`, `.venv` 밖의 파일이 모두 이 기기에 생긴 지 24시간이 안 됐다. mtime은 zip을 푼
    scaffolder가 옛 값으로 남기므로 ctime으로 잰다. 파일이 2000개를 넘으면 새 프로젝트로 보지 않는다.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

DAY = 24 * 60 * 60
MAX_FILES = 2000
SKIP_DIRS = {".git", "node_modules", ".venv"}
NOTE = (
    "이 디렉터리는 새 프로젝트로 보인다. project scope 설정이 없고, commit이 1개 이하이며, 파일이 모두 하루 안에 생겼다. "
    "사용자의 요청에서 프로젝트 종류가 드러나면 작업을 시작하기 전에 apply-project-template skill을 따른다. "
    "요청이 프로젝트와 무관하면 template을 제안하지 않는다."
)


def under(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip("/") + "/")


def commits(cwd: str) -> int | None:
    """HEAD까지의 commit 수를 2에서 끊어 센다. git repo가 아니면 0, git을 실행할 수 없으면 `None`."""
    try:
        inside = subprocess.run(["git", "-C", cwd, "rev-parse", "--is-inside-work-tree"],
                                capture_output=True, text=True, timeout=5)
        if inside.returncode != 0:
            return 0
        count = subprocess.run(["git", "-C", cwd, "rev-list", "--count", "--max-count=2", "HEAD"],
                               capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return int(count.stdout) if count.returncode == 0 else 0


def all_recent(cwd: str, cutoff: float) -> bool:
    seen = 0
    for dirpath, dirnames, filenames in os.walk(cwd):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name == ".DS_Store":
                continue
            seen += 1
            try:
                if seen > MAX_FILES or os.lstat(os.path.join(dirpath, name)).st_ctime < cutoff:
                    return False
            except OSError:
                return False
    return True


def suggestion(payload: dict, home: str, temp_roots: list[str], now: float) -> str | None:
    """새 프로젝트로 보이면 안내 문구, 아니면 `None`."""
    cwd = payload.get("cwd")
    if payload.get("source") != "startup" or not isinstance(cwd, str) or not os.path.isdir(cwd):
        return None
    cwd = os.path.realpath(cwd)
    if cwd == os.path.realpath(home) or any(under(cwd, os.path.realpath(r)) for r in temp_roots):
        return None
    if os.path.lexists(os.path.join(cwd, "CLAUDE.md")) or os.path.lexists(os.path.join(cwd, ".claude", "settings.json")):
        return None
    count = commits(cwd)
    if count is None or count > 1:
        return None
    return NOTE if all_recent(cwd, now - DAY) else None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    roots = [r for r in (os.environ.get("TMPDIR"), "/tmp") if r]
    note = suggestion(payload if isinstance(payload, dict) else {}, os.path.expanduser("~"), roots, time.time())
    if note:
        json.dump({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": note}}, sys.stdout,
                  ensure_ascii=False)


if __name__ == "__main__":
    main()
