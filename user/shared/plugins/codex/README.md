# codex (provenance-only)

This directory exists for provenance tracking only. The codex plugin is **not** vendored here.

## How it's actually installed

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

Run those slash commands inside a Claude Code session. Unlike the plugins from
`claude-plugins-official`, this one ships from a **third-party marketplace**
(`openai-codex`, published by OpenAI), so the `/plugin marketplace add` step is
required first — it records the marketplace under `extraKnownMarketplaces` in
`user/shared/settings.json`. The plugin then lives at
`~/.claude/plugins/cache/openai-codex/codex/<version>/` and is managed by Claude
Code's plugin CLI (`~/.claude/plugins/installed_plugins.json`).

`/codex:setup` verifies the toolchain. The plugin requires Node.js 18.18+ and
either a ChatGPT subscription or an OpenAI API key (kept machine-local — never
committed here).

## What the plugin ships

- Commands `/codex:review`, `/codex:adversarial-review` — read-only and steerable code reviews via Codex
- Commands `/codex:rescue`, `/codex:status`, `/codex:result`, `/codex:cancel` — delegate background tasks to Codex and manage them
- Command `/codex:setup` — verify installation and authentication
- Subagent `codex:codex-rescue` — available in `/agents`
- Optional Stop-hook review gate for targeted reviews

## Why a sidecar but no source

The plugin is managed by its marketplace; copying it here would duplicate what the
marketplace already manages — see [[../hookify]], [[../claude-md-management]],
[[../commit-commands]], and [[../skill-creator]] for the same pattern. It also
ships a Node/TypeScript companion runtime that can't be split sensibly, the same
reason [[../hookify]] is tracked whole.

This is the first tracked plugin from a non-Anthropic marketplace. The
`.provenance.json` next to this README pins the upstream commit so this repo's
`SOURCES.md` still records that codex is part of the user's setup.
