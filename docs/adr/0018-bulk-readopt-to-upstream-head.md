# 0018 — provenance 추적 항목 31건을 upstream HEAD로 일괄 갱신

`bin/check-updates`가 12개 소스 중 9개 저장소(항목 31건)의 pin 뒤처짐을 보고했다. blobless clone으로 추적 경로별 실제 변경 여부를 조사한 뒤, 사용자 지시로 전 항목을 `bin/adopt` 재실행해 upstream HEAD로 갱신했다. copied 항목은 파일 내용까지, inspired-by 항목은 pin만 갱신됐다.

## Context

조사 결과 두 부류로 갈렸다.

- **실질 변경 있음** — mattpocock/skills 6개 스킬, agent-skills의 react-view-transitions(18 커밋 규모 개편), agent-browser의 core, next.js 스킬 3개(next-cache-components-optimizer는 test-driven 루프로 재작성되어 파일 구성이 바뀜), Understand-Anything(36 커밋), github-mcp-server(98 커밋), context7(66 커밋), modelcontextprotocol/servers의 fetch·sequential-thinking(보안 의존성 bump).
- **pin만 뒤처짐** — claude-plugins-official의 5개 플러그인 등. 추적 경로에 커밋 0건이지만, 부분 갱신으로 pin이 갈라져 남는 것보다 전 항목을 같은 HEAD로 맞추는 쪽을 택했다.

mattpocock/skills는 조사(b137134f)와 실행 사이 HEAD가 이동해 실행 시점 HEAD(2ffb184f)로 pin했다.

## Consequences

- 재실행 후 `bin/check-updates`가 12개 소스 전부 up to date를 보고한다. `bin/sources-index`로 SOURCES.md를 재생성했다(183 entries / 61 sidecars).
- inspired-by 플러그인(understand-anything 등)의 실제 콘텐츠 갱신은 이 저장소가 아니라 `/plugin` 업데이트가 담당한다. 이 저장소에는 pin 이력만 쌓인다.
- **후속 결정 필요:** upstream context7 문서가 hosted HTTP 등록 헤더를 `CONTEXT7_API_KEY:`에서 `Authorization: Bearer`로 바꿔 권장한다. `user/shared/mcp/context7/README.md`의 등록 명령은 기존 방식이고 실제 머신 등록도 그 방식으로 살아 있어, 이번 갱신에서는 건드리지 않았다.

## References

- [[0003-adr-for-every-change]]
