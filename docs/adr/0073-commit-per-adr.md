# 0073 — ADR 단위 작업이 끝나면 묻지 않고 commit한다

지금까지는 사용자가 명시적으로 요청할 때만 commit했다. 2026-10-09 점검에서는 작업이 끝날 때마다 commit 요청을 따로 받아야 했고, 그 사이 변경이 working tree에만 남았다. 이 repo의 목적을 재현으로 정했으므로(ADR 0074) commit되지 않은 변경은 기기가 고장 나면 사라지는 상태다. 그래서 guardrail을 "ADR 하나에 해당하는 작업이 끝나고 `bin/check-integrity`가 깨끗하면 묻지 않고 commit한다"로 바꿨다. 이 repo는 변경마다 ADR을 쓰므로(ADR 0003) ADR이 곧 작업 단위다.

push는 바꾸지 않았다. 명시적 요청이 있을 때만 한다.

## Consequences

- commit할 때는 그 작업의 파일만 stage한다. `user/shared/settings.json`은 Claude Code가 실행 중에 고쳐 쓰므로, 무관한 변경이 섞이지 않게 경로를 지정해 stage한다.
- 원격에 없는 commit이 쌓일 수 있다. `bin/check-machine`이 그 수를 경고로 보고한다(ADR 0078).
