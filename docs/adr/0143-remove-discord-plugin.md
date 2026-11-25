# 0143 — discord plugin을 제거한다

사용자가 더는 쓰지 않는 discord plugin(ADR 0053)이 user scope에 켜져 있어서, 모든 세션에 MCP server 지시와 skill 두 개가 들어왔다. 그래서 `claude plugin uninstall discord@claude-plugins-official --scope user`로 지우고, `user/shared/plugins/discord/`의 선언도 지웠다.

## Consequences

- `README.md`의 범위 밖 목록에서 "Discord access policy" 항목을 뺐고, `docs/SECRETS.md`에서 `DISCORD_BOT_TOKEN` 행을 뺐다.
- 이 기기의 `~/.claude/channels/discord/`(bot token과 access 상태)도 지웠다. Discord 쪽 token은 아직 유효하므로, Developer Portal에서 token을 reset하거나 bot을 지우는 일은 사용자가 한다.
- 다시 쓰려면 ADR 0053의 절차대로 설치하고 `/discord:configure`로 token을 다시 넣는다.
