# 0108 — mattpocock/skills 밖의 29건을 2026-10-29 upstream으로 re-pin하고 `auto-editor-effects`는 보류

ADR 0107과 같은 날의 check-updates에서 outdated로 나온 나머지 10개 source의 항목 30건 가운데 29건을 각 비교 대상으로 옮겼다. `auto-editor-effects`는 upstream 최신 내용이 아직 release되지 않은 기능을 안내하므로 옛 pin에 남겼다.

## 바뀐 내용 (`copied` 4건)

- **`project-templates/nextjs/.claude/skills/core`** (agent-browser v0.41.0): MCP tool 하나를 stdio session 없이 실행하는 `agent-browser mcp call`이 생겼다. MCP `extraArgs`는 network, file, policy 관련 global flag를 거부한다. `plugin add`는 기본으로 `~/.agent-browser/config.json`에 쓴다. 숨은 element를 click할 때와 다른 session이 tab을 잡고 있을 때(`tab_locked`)의 실패가 문서에 들어갔다.
- **`deploy-to-vercel`** (agent-skills): 인증 없는 배포가 번들 script 대신 `npx vercel@latest deploy --temporary`를 쓴다. upstream이 지운 `resources/deploy.sh`, `resources/deploy-codex.sh`, `Archive.zip`은 local에서도 지워졌다. 이 경로는 이제 npm registry에 접근할 수 있어야 한다.
- **`react-view-transitions`** (agent-skills): Next.js 밖에서는 `react@canary` 대신 stable React 19.3 이상을 권한다. Next.js 안내는 그대로다.
- **`auto-editor-export`** (auto-editor): `final-cut-pro`와 `resolve` export의 `version` 옵션(11 또는 10)을 설명하는 문단과 예시가 들어갔다. 이 옵션은 release된 31.7.2에도 있다.

`/name` 참조와 Skill tool 호출 문구는 새로 생기거나 사라진 것이 없다.

## pin만 옮긴 항목 (25건)

- `inspired-by` 8건: plugin `understand-anything`, `commit-commands`, `hookify`, `remotion`과 MCP server `github`, `fetch`, `sequential-thinking`, `context7`이다. upstream 내용은 바뀌었지만 실제 동작은 marketplace와 `claude mcp add`가 정하므로 pin만 기록으로 옮겼다.
- 내용 변경이 없는 17건: plugin 5건, next.js template skill 5건, agent-skills 4건, auto-editor 2건, agent-browser `dogfood`이다.

vercel/next.js는 deep scan 뒤에 upstream HEAD가 `5a2d24ea`에서 `4c6a3fa4`로 움직였다. re-pin은 `4c6a3fa4`로 옮겼고, 그 구간에서도 next.js template skill 내용은 바뀌지 않았다.

## `auto-editor-effects` 보류

upstream `692cbbe`가 keyframe에 시점을 붙이는 `value@time` 문법을 문서에 넣었다. 같은 commit이 그 기능의 source code도 더하는데, 이 commit은 어떤 release tag에도 들어 있지 않다. 최신 release는 2026-10-02의 31.7.2다. 지금 옮기면 template skill이 설치된 auto-editor에서 실패하는 명령을 안내하므로 `5ab59aba`에 둔다. 31.7.2 다음 release가 나오면 re-pin하고 sidecar의 버전 요구 note를 고친다.

auto-editor의 tag는 `31.7.2`처럼 `v` 접두사가 없어서 `track: release`가 인식하지 못한다. 그래서 이 보류는 sidecar 설정으로 맡길 수 없고, 그 전까지 `check-updates`는 이 항목을 계속 changed로 보고한다.

## 들이기로 한 신규 항목

agent-browser에 새로 생긴 `.agents/skills/technical-writer`는 adopt하기로 했다. 원본이 vercel/chat에 있으므로 별도 ADR에서 다룬다.
