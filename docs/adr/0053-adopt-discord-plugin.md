# 0053 — discord plugin 설치와 provenance 기록

Claude Code 공식 marketplace의 `discord` plugin(v0.0.4, Apache-2.0)을 `/plugin install discord@claude-plugins-official`로 설치하고, `user/shared/plugins/discord/`에 provenance-only 항목으로 기록했다. Discord bot과 Claude Code 세션 사이에서 메시지를 주고받는 bridge다. 절차는 기존 plugin과 같지만 upstream 경로와 실행 방식이 다르다.

## Consequences

- provenance의 `--path`가 `external_plugins/discord`다. 지금까지 기록한 plugin은 전부 `plugins/<name>`이었다. marketplace manifest가 `"source": "./external_plugins/discord"`로 가리키기 때문이다. 나중에 새 commit으로 재고정할 때 이 경로를 확인해야 하며, README에도 같은 내용을 적어뒀다.
- 이 repo가 기록하는 plugin 중 처음으로 MCP server를 번들한다. plugin 자체의 `.mcp.json`이 Bun으로 `server.ts`(discord.js 기반)를 실행한다. `claude mcp add`로 등록하는 server가 아니므로 `user/shared/mcp/`의 대상이 아니고, `install.sh`가 출력하는 `claude mcp add` 안내에도 나오지 않는다.
- bot token은 `/discord:configure`가 `~/.claude/channels/discord/.env`에 쓰고, allowlist와 pairing 상태는 같은 디렉터리의 `access.json`에 남는다. 두 경로 모두 이 repo가 symlink하지 않으므로 "MCP secrets stay machine-local" guardrail을 그대로 지킨다.
- token을 설정하기 전에는 MCP server가 시작 직후 종료해서 세션마다 `plugin:discord:discord (CONNECTION_CLOSED)`가 뜬다. 설치 실패가 아니라 설정 전 정상 상태다.
- Bun이 PATH에 있어야 한다(현재 1.4.0 설치됨). "Dependencies stay minimal" guardrail은 이 repo의 도구인 Python 3 stdlib과 bash를 대상으로 하므로, plugin의 runtime 요구사항은 여기에 걸리지 않는다.
- `bin/check-integrity`는 clean이다.
