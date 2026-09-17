# 0055 — check-updates deep scan 결과 42개 항목을 재pin하고 next-partial-prefetching-optimizer를 adopt

2026-09-17 `check-updates --deep` 결과 12개 source 중 9개가 뒤처져 있었다. tracked path에 실제 commit이 있는 10개, upstream이 새로 추가한 skill 1개, pin만 뒤처진 31개를 한 번에 처리했다. `copied` 항목 7개는 로컬 파일이 갱신됐고(18개 파일, +509/-174), `inspired-by` 항목 3개와 pin-only 31개는 sidecar만 바뀌었다. `herdr`는 ADR 0051의 정책대로 master HEAD 대신 release tag v0.9.1(`065ef9d6`)에 고정했다. 이 시점에 `skills/herdr/SKILL.md`는 v0.9.1과 HEAD가 byte 단위로 같아 내용 손실은 없다.

## 실질 변경 요약

- **herdr** (copied): `herdr machine` 명령군, `--trust-repository`, `workspace close --group` 추가. idle/done 판정이 server 측 "seen" 상태 기준으로 바뀌었다. alternate-screen scrollback 복구가 가능하다고 문서화됐다.
- **agent-browser core, dogfood** (copied, nextjs template): 기본 대기 전략에서 `networkidle`이 제거되고 `domcontentloaded`, `--url`, `--text` 대기로 바뀌었다. `webmcp list` 문법이 `webmcp list <tool> --frame <id> --json`으로 바뀌었다. snapshot ref가 같은 문서 안 갱신에는 살아남는 것으로 의미가 바뀌었다. video 녹화에 `ffmpeg`(libvpx, libx264) 의존이 명시됐다.
- **next.js skill 4개** (copied, nextjs template, 모두 upstream #96471 공유): `next-cache-components-adoption`은 incremental pre-step에서 이전 static route를 완전히 migrate한다. `optimizer`와 `partial-prefetching-adoption`의 `rig-template.md`가 이름 있는 섹션 구조와 `CONTRACTS` 필드로 재구성됐다. `next-dev-loop`에 dev server 실행 중 `.next` 삭제 금지 gotcha가 추가됐다.
- **understand-anything, github-mcp-server, context7** (inspired-by): plugin 2.9.7, github tool 4개 추가, context7 OpenTelemetry와 OIDC auth 추가. 세 항목 모두 로컬 README의 등록 명령은 변경 없이 유효하다.

## 새로 adopt

`skills/next-partial-prefetching-optimizer`는 upstream이 이 구간에서 추가한 skill이다. Cache Components와 Partial Prefetching 도입 뒤 client navigation 경로 쌍을 `instant()` RED에서 GREEN으로 가는 test loop로 최적화한다. 이미 adopt한 cache-components의 adoption과 optimizer 쌍 패턴을 완성하므로 adopt했다. 이 skill이 참조하는 `next-cache-components-optimizer`와 `next-partial-prefetching-adoption`은 이미 있어 추가 chain은 없다. Next.js 16.3 이상을 요구한다.

## Consequences

- `copied` 항목 7개는 재동기화 전 로컬 사본이 pin과 byte 단위로 같았으므로 덮어쓴 로컬 수정은 없다.
- REMOVED 항목은 없었다. `check-integrity --strict`는 clean이다.
- herdr skill이 v0.9.x CLI 명령을 설명하므로, 로컬 herdr CLI가 v0.8.2라면 v0.9.1로 올려야 한다.
- 후속 사항 두 가지는 이 변경에 넣지 않았다. context7 README는 `CONTEXT7_API_KEY` header를 안내하지만 upstream README는 `Authorization: Bearer`만 안내한다(이 구간 이전부터 있던 표류). `user/shared/skills/synced/`는 Claude Code가 조직 skill을 `~/.claude/skills/`에 내려받은 것이 symlink를 타고 repo에 나타난 것이며, `.gitignore` 처리 여부는 별도 결정이 필요하다.
