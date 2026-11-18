# 0125 — OAuth로 로그인하는 MCP server는 claude.ai connector로 두고, Linear 선언을 지운다

MCP server가 Claude Code에 들어오는 길은 두 가지다. 기기에서 `claude mcp add`로 등록하고 이 repo에 선언하는 길과, claude.ai 계정에 connector로 추가하는 길이다. 어느 쪽에 둘지 정한 규칙이 없어서 Linear가 양쪽에 생겼다. server 종류로 위치를 정하기로 하고 그 규칙을 `user/shared/mcp/README.md`의 "Where a server goes" 절에 적었다. 이 규칙에 따라 Linear 선언을 지우고 ADR 0023을 대체한다.

## 규칙

| server | 위치 |
|---|---|
| 로컬에서 실행하는 stdio server | `claude mcp add`, 이 repo에 선언 |
| header에 secret을 넣는 원격 server | `claude mcp add`, 이 repo에 선언 |
| OAuth로 로그인하는 원격 server | claude.ai connector, 선언하지 않음 |

OAuth server는 connector로 할 수 없는 일이 있을 때만 직접 등록한다. read-only endpoint 같은 URL 변형이 필요하거나, 한 프로젝트에서만 쓰는 경우다.

## 경위

- 2026-11-18에 Carbon Design System MCP를 추가하려고 확인해 보니, 이미 `claude.ai Carbon Design System` connector로 연결돼 있었다. claude.ai 계정에 추가한 connector를 Claude Code가 가져온 것이다.
- 그때 `claude mcp list`에 나온 server는 이미 위 규칙대로 나뉘어 있었고, 어긋난 것은 Linear 하나였다. Linear는 양쪽 모두 인증이 안 된 상태였다.
  - 선언: `fetch`, `sequential-thinking` (stdio), `context7`, `github` (header secret), `linear` (OAuth)
  - connector: Carbon Design System, Notion, Gmail, Google Calendar, Claude Docs, Linear
- Carbon은 connector로 두고, repo에는 아무것도 더하지 않는다.

## 근거

Claude Code 공식 문서(code.claude.com/docs/en/mcp)의 "Use MCP servers from claude.ai" 절에서 확인했다.

- claude.ai 구독 계정으로 로그인한 Claude Code는 계정의 connector를 자동으로 가져온다. 그래서 새 기기에서도 로그인하면 connector가 생긴다. README의 Scope가 connector를 out of scope로 두는 이유와 같다.
- 모든 server를 직접 등록할 수는 없다. 문서는 이렇게 적는다. "Some Anthropic-hosted connectors, such as Microsoft 365, Gmail, and Google Calendar, don't support local OAuth from Claude Code because the upstream identity provider only accepts the redirect URL that claude.ai registered."
- 같은 URL의 server를 직접 등록하면 Claude Code는 그 등록을 쓰고, connector는 `/mcp`에서 숨김으로 표시한다.
- API key 같은 다른 인증 방법이 켜져 있으면 connector를 가져오지 않는다.

## Considered Options

- **모든 server를 직접 등록하고 repo에 선언한다.** ADR 0023의 방향을 넓히는 방법이다. Gmail과 Google Calendar는 직접 등록할 수 없다. OAuth 로그인을 기기마다 다시 해야 하고, desktop app 대화에서 쓰려면 connector를 따로 또 추가해야 한다.
- **server마다 그때그때 정한다.** 같은 server가 양쪽에 생기는 일이 Linear처럼 반복된다.
- **Linear만 직접 등록으로 남긴다.** ADR 0023이 고른 방법이다. read-only URL 변형은 README에 대안으로만 적혀 있었고 실제 등록은 full URL이었으므로, Linear를 예외로 둘 근거가 약했다.

## Consequences

- `user/shared/mcp/linear/`와 `docs/SECRETS.md`의 Linear 항목을 지웠다. 이 기기에서는 `claude mcp remove linear -s user`를 실행했다. Linear를 쓰려면 사용자가 claude.ai/customize/connectors에서 인증해야 한다.
- 쓰는 MCP의 전체 목록이 repo 한 곳에 모이지 않는다. connector 목록은 claude.ai 계정 설정에서 봐야 하고, repo만 읽어서는 Linear나 Carbon을 쓴다는 사실을 알 수 없다.
- 직접 등록한 `linear`를 지우자 `plugin:engineering:linear`가 `claude mcp list`에 나타났다. claude.ai에서 동기화되는 `engineering@synced` plugin이 같은 URL의 server를 갖고 있고, 공식 문서의 우선순위는 user scope, plugin, claude.ai connector 순서다. 같은 상황인 Notion은 이 session에서 connector tool이 그대로 쓰였으므로, 인증 안 된 plugin server가 connector를 가리지는 않는 것으로 보인다. Linear를 claude.ai에서 인증한 다음 `/mcp`에서 어느 쪽이 연결되는지 확인한다.
- Claude Code를 API key로 인증하는 기기에는 connector가 들어오지 않는다. 그런 기기에서 OAuth server가 필요해지면 그때 직접 등록한다.
- `docs/PROVENANCE.md`와 `user/shared/mcp/README.md`는 README만 두는 선언의 예로 claude.ai connector를 들고 있었다. 이제 connector는 선언하지 않으므로 그 예를 지웠다.
- `docs/migration-2026-08-31.md`는 지난 작업의 기록이므로 Linear 언급을 그대로 둔다.
