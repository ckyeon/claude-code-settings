# 0094 — git guard hook을 Python 3.9에서도 돌게 한다

`user/shared/hooks/guard-destructive-git.py`에 `from __future__ import annotations`를 더했다. hook이 실행하는 `python3`가 macOS 기본인 3.9.6이 되면서, 이 hook은 Bash 호출마다 `PreToolUse:Bash hook error`와 Traceback을 남기고 exit 1로 끝났다. 3.9는 `list[str] | None` 같은 annotation을 함수를 정의할 때 평가하다가 `TypeError`를 낸다. 이 import가 있으면 annotation을 평가하지 않는다.

## 경위

- ADR 0054(2026-09-17)는 설치된 경로에서 hook이 발동하는 것을 확인했다. 그때의 `python3`는 3.10 이상이었다.
- 2026-10-20 현재 `which -a python3`는 `/usr/bin/python3`(3.9.6) 하나만 낸다. `/opt/homebrew/bin`에는 2026-10-12 14:17에 만든 `python3.14` 같은 버전 붙은 링크만 있고 `python3`는 없다. 그날 Homebrew Python이 바뀌면서 `python3` 링크가 사라졌다고 추정한다. 그전 상태는 확인하지 못했다.
- Claude Code는 exit 2가 아닌 실패를 non-blocking으로 보고 명령을 그대로 실행한다. 그래서 그동안 이 guard는 아무 명령도 막지 못했다.

## Considered Options

- **이 Mac의 `python3` 링크를 복구한다.** 이 기계만 고쳐진다. 새 Mac에는 `/usr/bin/python3` 3.9만 있으므로 같은 문제가 다시 생긴다.

## Consequences

- 막아야 할 명령 5개(`reset --hard`, `clean -fd`, `checkout -- src/`, `checkout --force`, ref 없는 `restore`)와 통과시킬 명령 5개를 3.9.6과 3.14.8에서 돌렸다. 두 버전 모두 10개가 기대대로 나왔다.
- 이 hook을 시험하는 코드는 repo에 없다. `tests/run.sh`는 `bin/`와 `lib/`만 다룬다. 지금은 시험을 더하지 않는다. 이유는 셋이다.
  - 크래시는 Bash를 실행할 때마다 에러로 보이므로 시험 없이도 드러난다. 이번에도 그 에러를 보고 원인을 찾았다.
  - `tests/run.sh`는 PATH의 `python3`를 쓰므로 3.9에서 돌린다고 보장할 수 없다.
  - 이번 원인은 코드가 아니라 기계 환경의 변화였다.
- 조용히 생기는 위험은 판단 로직이 틀어지는 경우다. hook의 판단 로직을 다음에 고칠 때 두 가지를 함께 한다. 막을 명령과 통과시킬 명령의 case를 `tests/run.sh`에 넣고, CLAUDE.md의 "Run `tests/run.sh` after changing anything under `bin/` or `lib/`" guardrail에 `user/shared/hooks/`를 더한다.
