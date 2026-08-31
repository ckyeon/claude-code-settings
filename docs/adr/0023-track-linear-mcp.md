# 0023 — Linear MCP 서버를 직접 등록하고 README-only로 추적

Linear의 hosted MCP 서버(`https://mcp.linear.app/mcp`, Streamable HTTP, OAuth 2.1)를 `claude mcp add --scope user`로 직접 등록하고 `user/shared/mcp/linear/README.md`로 추적한다. 공개 소스 repo가 없어 `.provenance.json` sidecar는 두지 않는다 — 이 디렉터리의 첫 README-only MCP 항목이다.

## Context

`claude mcp list`에 이미 `claude.ai Linear`(scope: claude.ai config, 미인증)가 있었다. 계정에 붙은 커넥터라 이 repo가 등록·제거를 제어할 수 없고, 새 머신에서 `install.sh`가 리마인더로 재현하지도 못한다. 사용자는 repo가 관리하는 경로를 원했다.

## Considered Options

- **직접 등록 + repo 추적 (채택)** — `user/shared/mcp/` 형제 항목(context7, github)과 같은 워크플로우. 이름은 문서의 `linear-server` 대신 형제와 맞춰 `linear`.
- **기존 claude.ai 커넥터만 인증** — 설정이 없어 간단하지만 repo 밖이다. 기각.
- **read-only endpoint(`/mcp/readonly`)** — 에이전트의 쓰기를 막고 싶을 때의 변형. 기본은 full로 두고 README에 변형으로만 기록.

## Consequences

- 같은 backend를 가리키는 항목이 두 개(`linear`, `claude.ai Linear`) 공존한다. 둘 다 인증하면 Linear tool이 context에 두 벌 실린다. README에 "하나만 쓰고 커넥터는 미인증으로 둔다"를 명시했다 — github 항목이 plugin 경로와의 공존을 다룬 방식과 같다.
- sidecar가 없으므로 `bin/check-updates`와 `SOURCES.md`는 이 항목을 모른다. `install.sh`/`uninstall.sh`의 리마인더는 디렉터리 이름만 보므로(`lib/common.sh` `list_tracked_mcp_servers`) 정상적으로 `linear`를 나열한다 — 검증함.
- OAuth 인증은 `claude mcp add`가 하지 않는다. 세션 안에서 `/mcp` → `linear` → Authenticate를 사용자가 직접 한 번 거쳐야 한다. 토큰은 머신 로컬에만 남는다.
- API key를 bearer header로 넣는 비대화식 대안은 placeholder로만 README에 적었다. 실제 값은 이 repo에 들어오지 않는다.

## References

- [Linear MCP docs](https://linear.app/docs/mcp)
- [[0003-adr-for-every-change]]
