# 0069 — mattpocock 외 26개 항목을 2026-10-09 upstream으로 재pin

2026-10-09 `check-updates --deep` 결과 16개 source 중 12개가 뒤처져 있었다. 변경 29건, pin만 뒤처진 22건, upstream 신규 5건, upstream 삭제 1건이었다. 이 중 `mattpocock/skills`의 25건을 뺀 26건을 재pin했다. `mattpocock/skills`에는 `CONTEXT.md`를 `GLOSSARY.md`로 바꾸는 breaking 변경과 adopt한 skill의 삭제가 섞여 있어 따로 결정한다.

## 실질 변경 요약

copied 항목은 local 내용이 바뀌었다.

- **herdr** (v0.9.3, `7b116c05`): `herdr machine status --json`으로 machine 장애를 진단하는 방법이 추가됐다. `herdr machine reconnect`는 사용자가 SSH 인증을 직접 해야 하므로 agent가 실행하지 않는다는 규칙도 생겼다.
- **agent-browser `core`** (v0.38.2, `39a74c70`): `auth login`이 control을 고르는 기준과 실패 조건, `BROWSER_USE_PROFILE_ID`를 포함한 환경변수 3개, `webmcp invoke --frame`이 문서에 들어갔다. ADR 0063에서 release를 기다리며 보류한 항목이다.
- **auto-editor-effects** (`5ab59aba`): `pixelate`가 ramp 가능 필드에 추가됐다. auto-editor 31.7.0 이상이 필요하다.
- **next-cache-components-optimizer** (`5da8ef12`): FIX 단계가 inline recipe 대신 Next.js에 포함된 static shell guide를 먼저 읽도록 바뀌었다. `reference/patterns.md`와 `reference/real-app-patterns.md`는 upstream에서 삭제돼 local에서도 빠졌다.
- **next-partial-prefetching-adoption, next-partial-prefetching-optimizer** (`5da8ef12`): `rig-template.md`에서 Playwright `webServer`가 서버를 띄우고 내리도록 절차가 바뀌었다.

inspired-by 항목은 pin만 옮겼다.

- **github** (v2.0.2, `eb47a99d`): MCP protocol `2026-07-28` 이상에서 tool이 구조화된 출력을 반환한다. 등록 command는 그대로다.
- **context7** (`888e0134`): `@upstash/context7-mcp` 4.2.0부터 HTTP endpoint가 credential을 요구한다. 등록 command는 그대로다.
- **remotion** (`50993d0b`): skill 12개의 구성은 그대로다. preview를 먼저 열고 명시적 요청이 있을 때만 렌더링하라는 지시가 추가됐다.
- **understand-anything** (`ffa2f0a8`), **edit-by-transcript** (`43cfc566`): 표면적 변경이다.

pin만 뒤처진 15건은 내용 변경이 없다. `claude-plugins-official` 7건, auto-editor 3건, next.js 2건, `fetch`, `sequential-thinking`, `dogfood`다.

## 이번에 올리지 않은 항목

- **mattpocock/skills 25건**: 위 이유로 따로 결정한다.
- **신규 `plugins/math-proof`**: 연구 수준의 수학 증명용 plugin이라 쓸 일이 없다.
- **신규 `skills/next-bundle-optimizer`**: 2026-10-05에 생긴 뒤 6일과 7일에 연달아 수정됐다. 다음 점검에서 다시 본다.

## Consequences

- copied 6건은 재adopt 전 local 사본이 pin과 같았으므로 덮어쓴 local 수정은 없다.
- `project-templates/video/CLAUDE.md`와 `ffmpeg-recipes/references/cut-and-join.md`는 auto-editor 31.6.0에서 측정한 동작을 적고 있다. `auto-editor-effects`의 새 예시 `pixelate:1..64`는 31.7.0 이상에서만 동작하므로, video template 안에 기준 version이 둘이 됐다.
- upstream과 어긋난 local README 세 곳은 이번 변경 이전부터 있던 것이라 고치지 않았다. `understand-anything`의 graph 경로와 marketplace owner, `remotion`의 파일 수, `github`의 pin 표기다.
