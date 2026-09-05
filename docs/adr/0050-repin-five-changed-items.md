# 0050 — check-updates deep scan에서 실질 변경이 확인된 5개 항목을 재pin

2026-09-05 `check-updates --deep` 결과 10개 source가 뒤처져 있었고, 그중 tracked path에 실제 commit이 있는 항목은 5개였다. 다섯 개를 모두 재pin했다. 유일한 `copied` 항목인 agent-browser `core`(nextjs template)는 `record start`에 `--fps` flag가 추가돼 로컬 파일 3개가 갱신됐다. 나머지 넷은 `inspired-by`라 sidecar만 바뀌었다: github-mcp-server v1.12.0(governance toolset, enterprise scope, `per_page`가 `perPage`로 rename), Understand-Anything 2.9.5(incremental-update 파이프라인 재작업), context7 4.0.5와 sequential-thinking(둘 다 cosmetic). pin만 뒤처진 37개(mattpocock/skills 25, claude-plugins-official 5, next.js 4, herdr, fetch, dogfood)는 tracked path가 바뀌지 않아 그대로 두었다.

## Consequences

- github README의 검증 기준 commit을 `9205304f`로 올리고 scope 목록에 `admin:enterprise`를 추가했다. upstream `docs/scope-filtering.md`는 이 구간에서 바뀌지 않았으므로 "pinned commit에서 검증했다"는 문장은 새 pin에서도 참이다. 등록 명령은 다섯 항목 모두 변경 없이 유효하다.
- agent-browser `core`는 재동기화 전 로컬 사본이 pin과 byte 단위로 같았으므로 덮어쓴 로컬 수정은 없다.
- upstream 구조 변경(NEW, REMOVED)은 없었다. `check-integrity --strict`는 clean이다.
