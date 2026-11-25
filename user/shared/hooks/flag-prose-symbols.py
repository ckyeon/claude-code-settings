#!/usr/bin/env python3
"""Markdown 산문에서 절을 잇는 세미콜론과 화살표를 PostToolUse에서 찾아 Claude에게 알린다.

`~/.claude/rules/korean-writing.md`의 "문장 연결" 규칙은 기호가 숨긴 관계를 말로 쓰라고 한다.
그 기호 가운데 세미콜론과 화살표는 판단할 거리가 없으므로 쓰는 자리에서 기계로 찾는다.
막지는 않는다. 찾으면 파일의 줄 번호와 그 줄을 additionalContext로 내고, 못 찾으면 아무것도 내지 않는다.

검사 범위:
  - Write는 파일 전체를 본다.
  - Edit는 편집이 끝난 파일을 읽고, 그 안에서 new_string이 차지한 부분만 본다. 원래 있던 글은 지적하지 않는다.
    new_string이 파일에 여러 번 나오면 그 자리를 모두 본다.
    code fence나 frontmatter 안인지는 파일 전체를 보고 판정한다. new_string만 따로 보면
    기존 code fence 안을 고친 경우에 fence 표시 줄이 없어서 code를 산문으로 잘못 읽는다.

건너뛰는 곳: code fence, frontmatter, 표 줄(`|`로 시작), 인용 줄(`>`로 시작), inline code, 큰따옴표 안, 링크 주소.
기호와 건너뛰는 곳은 `bin/check-integrity`의 ADR 산문 검사와 같다. frontmatter는 ADR에 없어서 그 검사는 보지 않는다.

대시와 슬래시는 찾지 않는다. 규칙이 라벨 구분자, 제목 구분자, 경로, 단위에 이 기호를 허용하므로 기계로 가려내기 어렵다.
"""

from __future__ import annotations

import bisect
import json
import re
import sys

SYMBOL = re.compile(r"[→←⇒⇐↔]|->|=>|;")
"""절을 잇는 기호. `bin/check-integrity`의 PROSE_SYMBOL과 같다"""
EXEMPT_SPAN = re.compile(r"`[^`]*`|\"[^\"]*\"|“[^”]*”|\]\([^)]*\)")
"""줄 안에서 건너뛰는 부분. inline code, 큰따옴표 안, 링크 주소다"""
MAX_REPORTED = 20
"""알리는 줄 수의 상한. 넘으면 남은 줄 수만 적는다"""


def prose_mask(lines: list[str]) -> list[bool]:
    """줄마다 산문인지. code fence, frontmatter, 표 줄, 인용 줄은 산문이 아니다."""
    mask = []
    fenced = False
    in_front = bool(lines) and lines[0].rstrip() == "---"
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if in_front:
            mask.append(False)
            if index > 0 and line.rstrip() == "---":
                in_front = False
        elif stripped.startswith("```"):
            fenced = not fenced
            mask.append(False)
        else:
            mask.append(not fenced and not stripped.startswith(("|", ">")))
    return mask


def new_spans(tool_name: str, tool_input: dict, text: str) -> list[tuple[int, int]]:
    """이번 호출이 쓴 글이 파일 text에서 차지하는 자리. 각 자리는 [시작, 끝) 문자 위치다."""
    if tool_name == "Write":
        return [(0, len(text))]
    new = tool_input.get("new_string") or ""
    spans = []
    start = 0
    while new:
        found = text.find(new, start)
        if found < 0:
            break
        spans.append((found, found + len(new)))
        start = found + len(new)
    return spans


def findings(text: str, spans: list[tuple[int, int]]) -> list[tuple[int, str, list[str]]]:
    """spans 안의 산문에서 찾은 기호. (1부터 센 줄 번호, 줄, 기호 목록)을 줄 순서대로 돌려준다."""
    lines = text.split("\n")
    mask = prose_mask(lines)
    starts = [0]
    for line in lines[:-1]:
        starts.append(starts[-1] + len(line) + 1)
    hits: dict[int, set[str]] = {}
    for lo, hi in spans:
        first = bisect.bisect_right(starts, lo) - 1
        last = bisect.bisect_right(starts, max(lo, hi - 1)) - 1
        for index in range(first, last + 1):
            if not mask[index]:
                continue
            line = lines[index]
            begin = max(lo, starts[index]) - starts[index]
            end = min(hi, starts[index] + len(line)) - starts[index]
            # 건너뛸 부분을 같은 길이의 공백으로 바꿔 문자 위치를 유지한다.
            masked = EXEMPT_SPAN.sub(lambda m: " " * len(m.group(0)), line)
            found = [m.group(0) for m in SYMBOL.finditer(masked) if begin <= m.start() < end]
            if found:
                hits.setdefault(index, set()).update(found)
    return [(index + 1, lines[index], sorted(hits[index])) for index in sorted(hits)]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if not isinstance(payload, dict):
        return 0
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or ""
    if tool_name not in ("Write", "Edit") or not path.lower().endswith(".md"):
        return 0
    if isinstance(payload.get("tool_response"), str):
        # 실패한 호출이면 tool_response가 오류 문자열이다. 파일이 바뀌지 않았으므로 보지 않는다.
        return 0
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return 0
    found = findings(text, new_spans(tool_name, tool_input, text))
    if not found:
        return 0
    rows = [f"  {number}행 [{' '.join(symbols)}] {line.strip()[:160]}" for number, line, symbols in found[:MAX_REPORTED]]
    if len(found) > MAX_REPORTED:
        rows.append(f"  그 밖에 {len(found) - MAX_REPORTED}줄")
    context = (
        f"{path}의 Markdown 산문에서 절을 잇는 기호를 찾았다.\n"
        + "\n".join(rows)
        + "\n~/.claude/rules/korean-writing.md의 \"문장 연결\" 규칙대로 기호가 숨긴 관계를 말로 풀어 쓴다. "
        "코드, 타입 시그니처, 인용문처럼 규칙이 기호를 허용하는 자리라면 그대로 둔다."
    )
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": context,
    }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
