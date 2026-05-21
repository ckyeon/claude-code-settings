# claude-md-management (provenance-only)

This directory exists for provenance tracking only. The claude-md-management
plugin is **not** vendored here.

## How it's actually installed

```
/plugin install claude-md-management@claude-plugins-official
```

Run that slash command inside a Claude Code session. The plugin then lives at
`~/.claude/plugins/cache/claude-plugins-official/claude-md-management/<version>/`
and is managed by Claude Code's plugin CLI
(`~/.claude/plugins/installed_plugins.json`).

## What the plugin ships

- Skill `claude-md-improver` — audits and improves CLAUDE.md files
- Command `/revise-claude-md` — updates CLAUDE.md with session learnings

## Why a sidecar but no source

The plugin was briefly adopted via the **split** pattern (skill →
`user/shared/skills/claude-md-improver/`, command →
`user/shared/commands/revise-claude-md.md`) before we realized it was already
active via the official plugin marketplace. The duplicate was removed and
this directory replaced it; see [[../hookify]] for the same pattern applied
to a plugin that can't be split at all.

The `.provenance.json` next to this README pins the upstream commit so this
repo's `SOURCES.md` still records that claude-md-management is part of the
user's setup.
