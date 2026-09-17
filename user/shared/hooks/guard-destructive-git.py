#!/usr/bin/env python3
"""커밋하지 않은 작업을 한 번에 지우는 git 명령을 PreToolUse에서 막는다.

stdin으로 Bash tool의 입력 JSON을 받고, 막을 명령이면 permissionDecision이 deny인 JSON을 낸다.
막지 않을 때는 아무것도 내지 않는다. 판단은 명령 문자열만 보는 정적 검사라서 저장소 상태를 읽지 않는다.

막는 것:
  - `git reset --hard`, `git clean -f`: 언제나 넓게 지운다.
  - `git checkout`, `git restore`로 경로를 되돌리는데 (a) 어느 commit으로 되돌리는지 적지 않았거나
    (b) 경로가 디렉터리나 glob이라 여러 파일에 걸치는 경우.
  - `git checkout --force`: 지역 변경을 덮어쓰고 branch를 옮긴다.

막지 않는 것: `git checkout HEAD -- <파일>`처럼 되돌릴 commit과 파일을 둘 다 적은 명령, branch 이동, `git checkout -b`,
그리고 `git restore --staged`처럼 index만 되돌리고 작업 트리는 건드리지 않는 명령.
`git restore`는 위치 인자가 언제나 경로이므로 `--` 없이 파일 하나만 적어도 경로로 본다.
뮤테이션 검사처럼 고쳤다가 되돌리는 작업은 이 좁은 형태로 쓴다.

한계: 셸 스크립트 파일을 만들어 그 안에서 실행하면 실행하는 순간에는 명령 문자열이 보이지 않는다.
다만 그 파일을 만드는 heredoc은 Bash tool을 지나므로 만드는 자리에서 걸린다.
"""

import json
import re
import shlex
import sys

_SPLIT = re.compile(r"[\n;]|&&|\|\||\|")
"""명령 문자열을 검사 단위로 나누는 구분자"""
_GLOB = re.compile(r"[*?\[]")
_REF = re.compile(r"^[\w./@^~-]+$")
"""되돌릴 commit으로 볼 수 있는 인자. branch 이름, HEAD, SHA, origin/main 등이다"""


def fragments(command: str) -> list[list[str]]:
    """명령 문자열을 셸 구분자로 나누고 토큰으로 쪼갠다. 따옴표가 맞지 않으면 공백으로 쪼갠다."""
    pieces = []
    for piece in _SPLIT.split(command):
        try:
            pieces.append(shlex.split(piece))
        except ValueError:
            pieces.append(piece.split())
    return [tokens for tokens in pieces if tokens]


def git_arguments(tokens: list[str]) -> list[str] | None:
    """`git` 호출이면 전역 옵션을 뺀 인자 목록, 아니면 `None`. `sudo git`과 `git -C <경로>`도 `git` 호출이다."""
    while tokens and tokens[0] in ("sudo", "env", "command"):
        tokens = tokens[1:]
    if not tokens or tokens[0] != "git" and not tokens[0].endswith("/git"):
        return None
    arguments = tokens[1:]
    while arguments and arguments[0].startswith("-"):
        arguments = arguments[2:] if arguments[0] in ("-C", "-c") else arguments[1:]
    return arguments


def wide_revert(arguments: list[str]) -> str | None:
    """이 git 인자가 넓게 지우는 명령이면 막는 이유, 아니면 `None`."""
    if not arguments:
        return None
    subcommand, rest = arguments[0], arguments[1:]
    if subcommand == "reset" and ("--hard" in rest or "--keep" in rest):
        return "`git reset --hard`는 커밋하지 않은 변경을 저장소 전체에서 지운다"
    if subcommand == "clean" and any(option.startswith("-") and "f" in option.lstrip("-") for option in rest):
        return "`git clean -f`는 추적하지 않는 파일을 지운다"
    if subcommand not in ("checkout", "restore"):
        return None
    if subcommand == "checkout" and any(option in ("-f", "--force") for option in rest):
        return "`git checkout --force`는 지역 변경을 덮어쓴다"
    if subcommand == "restore" and _index_only(rest):
        return None
    paths, ref = _paths_and_ref(subcommand, rest)
    if not paths:
        return None
    if wide := [path for path in paths if path == "." or path.endswith("/") or _GLOB.search(path)]:
        return f"되돌릴 경로 {', '.join(wide)}가 파일 하나가 아니라 여러 파일에 걸친다"
    if ref is None:
        return "되돌릴 commit을 적지 않아 index 내용으로 되돌린다. 무엇으로 되돌아가는지 명령만 보고 알 수 없다"
    return None


def _index_only(rest: list[str]) -> bool:
    """`git restore --staged`처럼 index만 되돌리고 작업 트리는 건드리지 않는지. `--worktree`가 같이 있으면 아니다."""
    shorts = [token[1:] for token in rest if token.startswith("-") and not token.startswith("--")]
    staged = "--staged" in rest or any("S" in cluster for cluster in shorts)
    worktree = "--worktree" in rest or any("W" in cluster for cluster in shorts)
    return staged and not worktree


def _paths_and_ref(subcommand: str, rest: list[str]) -> tuple[list[str], str | None]:
    """되돌릴 경로 목록과, 어느 commit으로 되돌리는지. commit을 적지 않았으면 `None`이다."""
    if subcommand == "restore":
        return _restore_paths_and_source(rest)
    if "--" in rest:
        separator = rest.index("--")
        before, paths = rest[:separator], rest[separator + 1 :]
    else:
        # `--` 없이 경로를 적는 형태는 `git checkout .`처럼 경로로만 읽히는 인자가 있을 때만 본다.
        # `git checkout <이름>`은 branch 이동일 수 있어 경로로 단정하지 않는다.
        before = [token for token in rest if token.startswith("-")]
        paths = [token for token in rest if token == "." or token.endswith("/") or _GLOB.search(token)]
    refs = [token for token in before if not token.startswith("-") and _REF.match(token)]
    return paths, refs[0] if refs else None


def _restore_paths_and_source(rest: list[str]) -> tuple[list[str], str | None]:
    """`git restore`는 위치 인자가 언제나 경로다. 되돌릴 commit은 `--source=<ref>`, `--source <ref>`, `-s <ref>`로만 적는다."""
    paths, source = [], None
    tokens = iter(rest)
    for token in tokens:
        if token == "--":
            paths.extend(tokens)
        elif token.startswith("--source=") or token.startswith("-s="):
            source = token.split("=", 1)[1]
        elif token in ("--source", "-s"):
            source = next(tokens, None)
        elif not token.startswith("-"):
            paths.append(token)
    return paths, source


def main() -> int:
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (json.JSONDecodeError, AttributeError):
        return 0
    for tokens in fragments(command):
        arguments = git_arguments(tokens)
        if arguments is None:
            continue
        if (cause := wide_revert(arguments)) is None:
            continue
        reason = (
            f"{cause}. 이 모양의 명령이 커밋하지 않은 구현을 통째로 날린 적이 있다.\n"
            "먼저 커밋해 복구 지점을 만들고, 되돌릴 파일을 하나씩 `git checkout HEAD -- <파일>`로 지정한다.\n"
            "고쳤다가 되돌리는 검사는 커밋한 tree에서 파일 단위로 돌린다."
        )
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}, ensure_ascii=False))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
