# 0063 — nextjs template의 next.js skill 5개를 `63bb9d6a`로 재pin

2026-09-29 `check-updates --deep` 결과 16개 source 중 10개가 뒤처져 있었고, tracked path에 commit이 잡힌 항목은 8개였다. 이 중 로컬 내용을 바꿔야 하는 것은 vercel/next.js skill 4개뿐이어서, 같은 source의 pin-only 항목 `next-cache-components-optimizer`와 함께 5개를 `63bb9d6a`로 재pin했다. 나머지는 이유가 있어 이번에 올리지 않았다.

## 실질 변경 요약

- **next-dev-loop**: 브라우저를 기본으로 headless로 연다. 사용자가 UI를 보려 하면 harness의 inline browser를 쓰고, 로그인이나 기존 session 상태가 필요할 때만 headed로 다시 연다. "Report Next.js friction" 절이 추가됐는데, managed Next.js feedback instructions가 로드됐을 때만 동작한다. nextjs template에는 그 instructions가 없어서 이 절은 동작하지 않는다.
- **next-cache-components-adoption**: "headed 브라우저" 전제를 "`next-dev-loop`의 browser handoff"로 바꿨다. `next-dev-loop`과 같은 upstream commit에서 바뀌었으므로 함께 올려야 문구가 어긋나지 않는다.
- **next-partial-prefetching-optimizer**: `unstable_navigation()`과 `unstable_prefetch()`를 `navigation()`과 `prefetch()`로 이름을 바꿨다(Next.js PR #99241).
- **next-partial-prefetching-adoption, next-cache-components-adoption**: codemod `agents-md` 안내에서 `CLAUDE.md`를 뺐다.

## 이번에 올리지 않은 항목

- **agent-browser `core`**: 추가된 Browser Use 환경변수 4개 중 released CLI(v0.38.1)가 읽는 것은 `BROWSER_USE_API_KEY` 하나다. 다음 release 뒤에 올린다.
- **hyperframes**: README의 Pinning 절에 따라 marketplace의 sha를 따른다. `claude-plugins-official`은 아직 `8d2b6e7b`를 가리킨다.
- **herdr**: ADR 0051에 따라 stable release에만 pin한다. 최신 stable은 여전히 v0.9.1이고 `skills/herdr`의 diff도 비어 있다.
- **context7**와 그 밖의 pin-only 항목: 내용 변화가 없어 급하지 않다.

## Consequences

- 5개 모두 재동기화 전 로컬 사본이 pin과 같았으므로 덮어쓴 로컬 수정은 없다.
- `check-updates --deep`은 herdr처럼 pin이 head의 조상이 아니면 내용이 같아도 "changed"로 보고하고, hyperframes처럼 upstream HEAD가 아닌 기준을 따르는 항목도 계속 outdated로 보고한다. 도구 수정은 별도 결정으로 다룬다.
