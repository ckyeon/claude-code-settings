# 0109 — technical-writer는 지금 들이지 않고 필요할 때 vercel/chat에서 들인다

ADR 0108의 check-updates에서 agent-browser에 새로 생긴 `.agents/skills/technical-writer`를 검토했다. SDK, library, framework의 개발자 문서를 쓰고 리뷰하는 skill이다. 사용자가 그런 문서를 쓸 일이 거의 없다고 해서 들이지 않는다.

## 검토한 내용

- 원본은 vercel/chat의 `.agents/skills/technical-writer`이고 license는 MIT다. agent-browser는 이것을 복사했고, 두 사본이 다른 곳은 description의 예시 사이트 한 줄이다. 두 repo 모두 자기 문서를 쓸 때 쓰는 contributor skill로 둔다(`metadata.internal: true`).
- 들인 mattpocock skill 가운데 사람이 읽는 개발자 문서를 다루는 것은 없다. `writing-for-agents`는 agent가 읽는 문서를, `pr`은 PR 본문을 다룬다.
- 이미 활성화된 plugin skill `engineering:documentation`이 같은 영역을 다룬다. 그 원칙 5개는 technical-writer에 더 자세히 들어 있고, technical-writer에는 source로 주장을 검증하는 절차와 편집 절차가 더 있다. user scope에 함께 두면 호출 조건이 겹친다.

## Consequences

- agent-browser의 pin이 `1453dd37`로 옮겨져 이 항목은 pin보다 먼저 생긴 것이 됐다. 그래서 `check-updates`는 이 항목을 다시 알리지 않는다.
- 필요해지면 vercel/chat에서 `copied`로 들이고, 그때 `engineering:documentation`과 호출 조건이 겹치는 문제를 다시 본다.
