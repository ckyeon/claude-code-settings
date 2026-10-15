# Secrets this setup needs

Secret values are out of scope: they are entered per machine and never committed. This file declares which secrets exist, what uses each, and where each goes, so a new machine can be completed without guessing.

| Secret | Used by | Where it goes | Details |
|---|---|---|---|
| context7 API key | `context7` MCP server | The `Authorization: Bearer` header of the `claude mcp add` command, which stores it in `~/.claude.json` | [`user/shared/mcp/context7/README.md`](../user/shared/mcp/context7/README.md) |
| GitHub personal access token | `github` MCP server | The `Authorization: Bearer` header of the `claude mcp add` command, which stores it in `~/.claude.json` | [`user/shared/mcp/github/README.md`](../user/shared/mcp/github/README.md) covers the token type and scopes |
| `DISCORD_BOT_TOKEN` | `discord` plugin | `~/.claude/channels/discord/.env`, written by `/discord:configure <token>` | [`user/shared/plugins/discord/README.md`](../user/shared/plugins/discord/README.md) |
| `GEMINI_TRANSCRIBE_API_KEY` | `transcribe` skill | An environment variable in the shell that starts Claude Code | [`user/shared/skills/transcribe/SKILL.md`](../user/shared/skills/transcribe/SKILL.md) |
| Claude long-lived OAuth token | The mirror arms (`on-mirror`, `off-rules`) of `evals/run.py` | The macOS Keychain item `claude-code-evals-oauth-token`, stored with `security add-generic-password -a "$USER" -s claude-code-evals-oauth-token -w` (it prompts for the value). The `CLAUDE_CODE_OAUTH_TOKEN` environment variable overrides it | Created by `claude setup-token`. See [`evals/README.md`](../evals/README.md) |
| OpenAI credentials | `codex` plugin | The Codex CLI's own sign-in, checked by `/codex:setup`. Either a ChatGPT subscription or an OpenAI API key | [`user/shared/plugins/codex/README.md`](../user/shared/plugins/codex/README.md) |

## Sign-ins with nothing to paste

- **Claude account.** Signing in to Claude Code also brings the skills, plugins, and connectors synced from claude.ai.
- **Linear.** The `linear` MCP server uses OAuth through `/mcp`. See [`user/shared/mcp/linear/README.md`](../user/shared/mcp/linear/README.md).

## Limits

`bin/check-machine` does not look at secrets. A machine can pass it with a key missing, and the gap then shows up when the server, plugin, or skill is first used.

When a declaration starts needing a secret, add its row here in the same change.
