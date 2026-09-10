# discord (provenance-only)

This directory exists for provenance tracking only. The discord plugin is **not** vendored here.

## How it's actually installed

```
/plugin install discord@claude-plugins-official
```

Run that slash command inside a Claude Code session. The plugin then lives at
`~/.claude/plugins/cache/claude-plugins-official/discord/<version>/` and is
managed by Claude Code's plugin CLI (`~/.claude/plugins/installed_plugins.json`).

## What the plugin ships

- MCP server `plugin:discord:discord` — a Discord bot bridge (`server.ts` on discord.js), declared in the plugin's own `.mcp.json`
- Skill `/discord:configure` — saves the bot token and reports channel status
- Skill `/discord:access` — pairing approvals, allowlists, DM and guild-channel policy

## The upstream path differs from every other tracked plugin

The others pin `plugins/<name>`. This one pins `external_plugins/discord`,
which is where the marketplace manifest points (`"source": "./external_plugins/discord"`).
Check that path before re-pinning to a newer commit.

## Runtime prerequisites, machine-local and not managed by this repo

- **Bun.** The MCP server runs as `bun run --cwd ${CLAUDE_PLUGIN_ROOT} start`, so Bun must be on `PATH`.
- **A Discord bot token.** `/discord:configure <token>` writes `DISCORD_BOT_TOKEN=...` to `~/.claude/channels/discord/.env`, and access state lives next to it in `access.json`. Neither path is symlinked from this repo, so the token stays out of version control. That matches the "MCP secrets stay machine-local" guardrail in `CLAUDE.md`, which `user/shared/mcp/` follows for servers registered with `claude mcp add`.

Until that token exists the MCP server exits at startup, which shows up as
`plugin:discord:discord (CONNECTION_CLOSED)` when a session begins.

## Why a sidecar but no source

The plugin is a Bun and TypeScript MCP server plus two skills, all managed by
the official plugin marketplace. Copying it here would duplicate what the
marketplace already manages. See [[../hookify]] for the same reasoning.

The `.provenance.json` next to this README pins the upstream commit so this
repo's `SOURCES.md` still records that discord is part of the user's setup.
