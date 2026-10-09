# 0080 — 구조 scan의 규칙을 `lib/structure.py`에 모으고, pin이 섞였을 때의 오보를 고친다

리뷰(ADR 0079와 같은 리뷰)에서 ADR 0070의 구조 scan에 두 가지가 나왔다.

- **pin이 섞이면 잘못 보고했다.** 한 source의 항목들이 서로 다른 pin에 있을 때, 이미 최신인 항목의 옆에 생긴 skill이 `NEW … (outside tracked dirs)`로 나왔다. 그 디렉터리는 추적 디렉터리이고, 그 skill은 거기 있는 항목의 pin을 옮길 때 이미 보고된 것이다. scan 범위를 뒤처진 항목의 부모로만 정하고, 제외 목록에는 추적 경로만 넣었기 때문이다. 이제 추적 경로의 부모 디렉터리 바로 아래에 생긴 항목은 두 번째 pass에서 뺀다. 그런 항목은 그 디렉터리에 있는 항목의 pin을 기준으로 첫 번째 pass가 보고한다.
- **같은 code가 두 도구에 있었다.** `bin/adopt`와 `bin/check-updates`가 marker 비교를 각자 갖고 있어서 위 결함도 두 곳에 있었다. `lib/structure.py`로 옮기고 두 도구가 import한다.

`bin/adopt`는 지금까지 자기가 옮기는 항목의 경로만 알았다. 그래서 `skills/productivity`의 항목을 옮길 때 `skills/engineering`에 생긴 skill을 "outside tracked dirs"로 경고했다. 이제 repo의 sidecar를 읽어 같은 source에서 추적하는 경로를 모두 알고 판정한다.

## Consequences

- ADR 0070의 완료 기준 3, 곧 "pin 이전부터 있던 adopt하지 않은 skill은 보고하지 않는다"가 pin이 섞인 경우에도 성립한다.
- 추적 경로가 repo 최상위에 있으면 그 부모는 최상위 디렉터리다. 최상위에 새로 생긴 항목은 첫 번째 pass가 보고하고, 더 깊은 곳에 생긴 것은 두 번째 pass가 계속 보고한다.
- test 2개를 추가했다. 고치기 전의 도구로 같은 test를 돌리면 3개가 실패한다.
