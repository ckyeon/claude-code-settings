#!/usr/bin/env python3
"""Claude가 쓰는 산문에서 절을 잇는 세미콜론과 화살표를 찾아 알린다.

`~/.claude/rules/korean-writing.md`의 "문장 연결" 규칙은 기호가 숨긴 관계를 말로 쓰라고 한다.
그 기호 가운데 세미콜론과 화살표는 판단할 거리가 없으므로 쓰는 자리에서 기계로 찾는다.
못 찾으면 아무것도 내지 않는다. 두 자리에서 돈다.

  - Write와 Edit의 PostToolUse: Markdown 파일(`*.md`)을 본다. 막지는 않고, 찾은 줄을 additionalContext로 알린다.
  - Bash의 PreToolUse: `git commit`의 message와 `gh pr create`, `gh pr edit`의 제목과 본문을 본다(ADR 0140).
    찾으면 명령을 막는다(deny). PR은 게시되는 순간 알림이 나가므로, 실행한 뒤에 알리면 늦다.
    글은 `-m`, `--title`, `--body` 같은 옵션 값, heredoc 본문, `-F`와 `--body-file`이 가리키는 파일에서 읽는다.
    편집기로 쓰는 message처럼 명령 문자열에 없는 글은 보지 못한다.

Markdown 파일의 검사 범위:
  - Write는 파일 전체를 본다.
  - Edit는 편집이 끝난 파일을 읽고, 그 안에서 new_string이 차지한 부분만 본다. 원래 있던 글은 지적하지 않는다.
    new_string이 파일에 여러 번 나오면 그 자리를 모두 본다.
    code fence나 frontmatter 안인지는 파일 전체를 보고 판정한다. new_string만 따로 보면
    기존 code fence 안을 고친 경우에 fence 표시 줄이 없어서 code를 산문으로 잘못 읽는다.

건너뛰는 곳: code fence, frontmatter, 표 줄(`|`로 시작), 인용 줄(`>`로 시작), inline code, 큰따옴표 안, 링크 주소.
`bin/check-integrity`도 ADR 산문을 이 파일의 `findings()`로 판정한다(ADR 0139). 이 파일을 고치면 그 검사도 함께 바뀐다.

대시와 슬래시는 찾지 않는다. 규칙이 라벨 구분자, 제목 구분자, 경로, 단위에 이 기호를 허용하므로 기계로 가려내기 어렵다.
"""

from __future__ import annotations

import bisect
import json
import os
import re
import shlex
import sys

SYMBOL = re.compile(r"[→←⇒⇐↔]|->|=>|;")
"""절을 잇는 기호"""
EXEMPT_SPAN = re.compile(r"`[^`]*`|\"[^\"]*\"|“[^”]*”|\]\([^)]*\)")
"""줄 안에서 건너뛰는 부분. inline code, 큰따옴표 안, 링크 주소다"""
MAX_REPORTED = 20
"""알리는 줄 수의 상한. 넘으면 남은 줄 수만 적는다"""
RULE_HINT = ("~/.claude/rules/korean-writing.md의 \"문장 연결\" 규칙대로 기호가 숨긴 관계를 말로 풀어 쓴다. "
             "코드, 타입 시그니처, 인용문처럼 규칙이 기호를 허용하는 자리라면 backtick이나 큰따옴표로 감싸 표시한다.")

HEREDOC = re.compile(r"<<-?[ \t]*(['\"]?)([A-Za-z_]\w*)\1([^\n]*)\n((?:.*?\n)??)[ \t]*\2[ \t]*(?=\n|$)", re.S)
"""heredoc 하나. 여는 연산자, 그 줄의 나머지, 본문, 닫는 줄이다"""
MARKER = "__HEREDOC_{}__"
SEPARATORS = ";&|()\n"
"""명령을 나누는 문자. 이 문자로만 된 낱말은 명령 사이의 구분자다"""
ENV_ASSIGNMENT = re.compile(r"[A-Za-z_]\w*=")
COMMAND_OPTIONS = {
    "git": {"-m": "commit message", "--message": "commit message", "-F": "file", "--file": "file"},
    "gh": {"-t": "PR 제목", "--title": "PR 제목", "-b": "PR 본문", "--body": "PR 본문",
           "-F": "file", "--body-file": "file"},
}
"""검사하는 명령의 옵션과, 그 값이 무엇인지. file은 값이 글이 든 파일 경로라는 뜻이다"""
HEREDOC_LABEL = {"git": "commit message", "gh": "PR 본문"}


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


def report_rows(found: list[tuple[int, str, list[str]]]) -> list[str]:
    """찾은 기호를 알릴 줄들. MAX_REPORTED를 넘으면 남은 줄 수만 적는다."""
    rows = [f"  {number}행 [{' '.join(symbols)}] {line.strip()[:160]}" for number, line, symbols in found[:MAX_REPORTED]]
    if len(found) > MAX_REPORTED:
        rows.append(f"  그 밖에 {len(found) - MAX_REPORTED}줄")
    return rows


def split_heredocs(command: str) -> tuple[str, list[str]]:
    """heredoc 본문을 떼어 낸 명령과 본문 목록. 떼어 낸 자리에는 MARKER를 둔다.

    본문을 먼저 떼어 내야 본문 안의 따옴표 때문에 shlex가 실패하지 않는다.
    """
    bodies: list[str] = []

    def cut(match: re.Match) -> str:
        bodies.append(match.group(4))
        return MARKER.format(len(bodies) - 1) + match.group(3)

    return HEREDOC.sub(cut, command), bodies


def commands(skeleton: str) -> list[list[str]]:
    """heredoc을 떼어 낸 명령 문자열을 명령마다 낱말 목록으로 나눈다. 따옴표가 맞지 않으면 빈 목록이다."""
    lexer = shlex.shlex(skeleton.replace("\\\n", " "), posix=True, punctuation_chars=SEPARATORS)
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    result: list[list[str]] = []
    current: list[str] = []
    try:
        for word in lexer:
            if word and all(c in SEPARATORS for c in word):
                if current:
                    result.append(current)
                current = []
            else:
                current.append(word)
    except ValueError:
        return []
    if current:
        result.append(current)
    return result


def command_texts(words: list[str], bodies: list[str], cwd: str) -> list[tuple[str, str]]:
    """명령 하나가 남길 글. (무슨 글인지, 글) 목록이고, 검사할 명령이 아니면 빈 목록이다."""
    while words and (words[0] in ("sudo", "env", "command") or ENV_ASSIGNMENT.match(words[0])):
        words = words[1:]
    if not words:
        return []
    program = os.path.basename(words[0])
    if program == "git":
        args = words[1:]
        while args and args[0].startswith("-"):
            args = args[2:] if args[0] in ("-C", "-c") else args[1:]
        if not args or args[0] != "commit":
            return []
        args = args[1:]
    elif program == "gh" and words[1:3] in (["pr", "create"], ["pr", "edit"]):
        args = words[3:]
    else:
        return []
    options = COMMAND_OPTIONS[program]
    texts: list[tuple[str, str]] = []
    index = 0
    while index < len(args):
        word = args[index]
        following = args[index + 1] if index + 1 < len(args) else None
        if word in options:
            label, value = options[word], following
            index += 1
        elif word.startswith("--") and word.split("=", 1)[0] in options:
            label, value = options[word.split("=", 1)[0]], word.split("=", 1)[1]
        elif program == "git" and re.fullmatch(r"-[a-zA-Z]+m", word):
            label, value = "commit message", following  # -am처럼 m으로 끝나는 짧은 옵션 묶음
            index += 1
        elif program == "git" and word.startswith("-m") and len(word) > 2:
            label, value = "commit message", word[2:]
        else:
            label, value = None, None
        index += 1
        if value is None or "__HEREDOC_" in value:
            continue  # heredoc 본문은 아래에서 따로 본다
        if label == "file":
            if value == "-":
                continue
            try:
                with open(os.path.join(cwd, os.path.expanduser(value)), encoding="utf-8") as f:
                    texts.append((HEREDOC_LABEL[program], f.read()))
            except (OSError, UnicodeDecodeError):
                pass
        else:
            texts.append((label, value))
    for number in sorted({int(n) for word in words for n in re.findall(r"__HEREDOC_(\d+)__", word)}):
        texts.append((HEREDOC_LABEL[program], bodies[number]))
    return texts


def check_command(command: str, cwd: str) -> int:
    """Bash 명령이 남길 commit message와 PR 글에서 기호를 찾으면 명령을 막는다."""
    if "commit" not in command and "gh" not in command:
        return 0
    skeleton, bodies = split_heredocs(command)
    blocks = []
    for words in commands(skeleton):
        for label, text in command_texts(words, bodies, cwd):
            found = findings(text, [(0, len(text))])
            if found:
                blocks.append(f"{label}의 산문에서 절을 잇는 기호를 찾았다.\n" + "\n".join(report_rows(found)))
    if not blocks:
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "\n".join(blocks) + "\n" + RULE_HINT + " 고친 다음 명령을 다시 실행한다.",
    }}, ensure_ascii=False))
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if not isinstance(payload, dict):
        return 0
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}
    if tool_name == "Bash":
        return check_command(tool_input.get("command") or "", payload.get("cwd") or os.getcwd())
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
    context = f"{path}의 Markdown 산문에서 절을 잇는 기호를 찾았다.\n" + "\n".join(report_rows(found)) + "\n" + RULE_HINT
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": context,
    }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
