# 0075 — `bin/` 도구의 test를 `tests/run.sh`에 둔다

`bin/`의 도구 네 개에는 test가 없었다. ADR 0039와 ADR 0070 때 가짜 upstream을 만들어 경계 사례를 확인했지만 매번 임시로 만들고 버렸다. 2026-10-09의 누락도 도구의 사각지대에서 나왔다. 같은 fixture를 수정 때마다 다시 만드는 대신 repo에 두기로 했다.

`tests/run.sh` 하나로 실행한다. 임시 디렉터리에 `bin/`과 `lib/`의 사본, 가짜 `file://` upstream을 만들고 그 안에서 도구를 돌린다. `HOME`을 빈 디렉터리로 바꿔서 실행하므로 실제 repo, `~/.claude`, network를 건드리지 않는다. 의존성은 bash 3.2와 Python 3 stdlib뿐이다.

처음 담은 것은 기존 동작을 확인하는 40개 check다. `bin/adopt`의 첫 adopt와 재pin, upstream이 지운 파일의 정리, 구조 변화 경고, `bin/check-updates`의 fast와 deep 판정, `bin/check-integrity`의 참조 검사와 sidecar 검증을 다룬다.

## Considered Options

- **지금처럼 수정할 때마다 임시로 검증하기**: 같은 fixture를 반복해서 만들고, 예전에 확인한 동작이 깨져도 알 수 없다.
- **Stop hook에서 돌리기**: 넣지 않았다. clone을 여러 번 해서 session이 끝날 때마다 돌리기에는 무겁고, 도구를 고치지 않은 session에서는 의미가 없다. `CLAUDE.md`의 guardrail이 `bin/`이나 `lib/`을 고친 뒤 돌리라고 지시한다.

## Consequences

- `bin/check-integrity`는 `~/.claude/plugins/cache`의 skill도 참조 대상으로 인정한다. test는 `HOME`을 바꿔 이 경로를 비우므로, plugin skill로 풀리는 참조는 test에서 다루지 않는다.
- test가 실제로 회귀를 잡는지는 도구 사본을 두 군데 고쳐서 확인했다. 중첩 항목을 묶는 조건을 없애자 4개가, `--strict` 처리를 없애자 1개가 실패했다.
