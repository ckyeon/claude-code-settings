# 0020 — 누락된 의존 스킬 3개를 upstream HEAD로 adopt

`bin/check-integrity`가 보고한 끊긴 참조 8건을 해소하기 위해 `codebase-design`, `domain-modeling`, `grilling`을 mattpocock/skills@8b78b531에서 adopt했다. wrapper만 가져오고 위임 대상을 빼놓은 상태였다.

## Context

기존 7개 스킬 중 4개가 설치되지 않은 스킬을 참조하고 있었다.

| 참조하는 쪽 | 참조 대상 |
|---|---|
| `grill-with-docs` | `grilling`, `domain-modeling` |
| `improve-codebase-architecture` | `codebase-design`, `grilling`, `domain-modeling` |
| `tdd` | `codebase-design` |
| `triage` | `grilling`, `domain-modeling` |

`grill-with-docs`는 특히 본문 전체가 위임 한 줄뿐이라 완전히 죽어 있었다.

원인은 upstream의 카테고리 배치다. adopt가 `skills/engineering/`만 훑었는데 `grilling`은 `skills/productivity/`에 있다. `codebase-design`과 `domain-modeling`은 `skills/engineering/`에 있었는데도 함께 가져오지 않았다 — 어느 쪽이든 위임 관계를 확인하는 절차가 없었다는 뜻이다.

upstream `grill-with-docs`의 현재 내용도 같은 한 줄이라, 이는 upstream 결함이 아니라 이 저장소의 부분 adopt 문제다.

## Considered Options

**`grill-with-docs`를 버리는 안**도 있었다. 하지만 나머지 3개 스킬(`improve-codebase-architecture`, `tdd`, `triage`)이 같은 대상을 참조하므로, 버려도 끊긴 참조 6건이 남는다. 의존 대상 adopt가 유일하게 전체를 해소한다.

사용자 지시("레포 최신 상태를 기반으로 처리")에 따라 pin은 특정 시점이 아니라 upstream HEAD로 잡았다.

## Consequences

- 스킬 10개 → 13개. 세 스킬 모두 leaf라(추가 스킬 참조 없음) 전이 의존은 여기서 닫힌다.
- `bin/check-integrity` 오류 8건 → 0건.
- 세 항목 모두 `8b78b531`로 pin돼 기존 mattpocock/skills 항목들과 같은 HEAD를 공유한다([[0018-bulk-readopt-to-upstream-head]]가 맞춰둔 정렬 유지).
- 상시 로드되는 description이 3개 늘지만 총량은 여전히 1천 토큰 미만이라 무시할 수준이다.
- 재발 방지는 `bin/check-integrity`를 adopt 후 실행하는 것으로 CLAUDE.md에 명시했다.

## References

- [[0019-static-integrity-checker]] — 이 결함을 찾아낸 검사기
- [[0018-bulk-readopt-to-upstream-head]]
- [[0003-adr-for-every-change]]
