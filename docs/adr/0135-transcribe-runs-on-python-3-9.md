# 0135 — transcribe.py가 macOS 시스템 python3(3.9)에서도 돈다

`transcribe.py`에 `from __future__ import annotations`를 넣고, 실행 때 평가되는 type alias `Seg`의 `str | None`을 `Optional[str]`로 바꿨다. SKILL.md가 적은 `python3 ~/.claude/skills/transcribe/scripts/transcribe.py`가 macOS 시스템 python3에서 그대로 돈다.

## 경위

- macOS 시스템 python3는 3.9.6이다. 그 python3로 실행하면 첫 함수 정의의 `float | None`에서 `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`로 끝났다. 그래서 다른 Python 경로를 따로 아는 세션만 전사를 돌릴 수 있었다.
- 이 repo의 다른 Python 파일(`bin/apply-template`, `bin/suggest-setting`, `user/shared/hooks/`의 두 hook)은 이미 `from __future__ import annotations`를 쓴다.

## 결정

- **SKILL.md에 최소 버전을 적지 않고 스크립트를 고친다.** 기기마다 새 Python의 경로가 달라서 명령 하나로 적을 수 없다.
- `__future__` import는 annotation만 늦게 평가한다. `Seg`는 module 수준의 대입이라 3.9에서 그대로 평가되므로 `typing.Optional`로 썼다.

## Consequences

- Python 3.9.6과 3.14.10에서 `--help`와 ADR 0133의 scratch 검사(파싱, 재시도, 청크 캐시, 앵커 오프셋)를 모두 통과했다.
