# 0037 — check-updates가 upstream 구조 변화(신규/삭제 스킬)도 보고

`bin/check-updates --deep`은 지금까지 채택한 path만 봤기 때문에, 소스 repo에 새 스킬이 생기면 오히려 전부 pin-only로 조용히 넘어가는 사각지대가 있었다 (예: mattpocock/skills에 13번째 스킬이 추가돼도 "실질 변경 없음"으로 보고). 소스 repo를 채택했다는 것은 그 repo 자체를 신뢰한다는 뜻이므로, deep pass가 추적 path의 부모 디렉터리를 pin 시점과 HEAD 시점에서 `git ls-tree`로 비교해 `NEW`(신규) / `REMOVED`(삭제, 채택한 항목이면 `** adopted here **` 표시)를 보고하도록 확장했다. pin 대비 비교라서 pin 이전부터 있었지만 일부러 채택하지 않은 항목은 잡음으로 뜨지 않고, whole-repo 항목(`path: "."`)은 git log가 이미 전체를 덮으므로 제외한다. `/check-updates` 스킬의 판단 레이어도 확장: subagent가 NEW 항목의 SKILL.md를 읽어 채택 가치를 판단하고, REMOVED 항목은 rename/폐기 여부를 조사한다.

## Considered Options

- 전체 repo 커밋 로그 요약까지 확장 — phaser처럼 스킬이 거대 repo에 얹힌 경우 잡음이 지배해 기각. "추적 path의 부모 디렉터리" 범위가 신뢰 범위와 일치한다.
- 스킬(판단 레이어)에서만 처리 — 구조 비교는 결정적 작업이므로 스크립트에 두는 것이 이 repo의 역할 분담(스크립트=사실, 스킬=판단)에 맞다.
