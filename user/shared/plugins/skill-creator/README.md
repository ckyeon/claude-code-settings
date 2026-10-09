# skill-creator (declared)

This directory is a declaration. The skill-creator plugin is **not** vendored here.

## How it's actually installed

```
/plugin install skill-creator@claude-plugins-official
```

Run that slash command inside a Claude Code session. The plugin then lives at
`~/.claude/plugins/cache/claude-plugins-official/skill-creator/<version>/` and is
managed by Claude Code's plugin CLI (`~/.claude/plugins/installed_plugins.json`).

## What the plugin ships

- Create new skills from scratch
- Update and optimize existing skills
- Run evals to test skill performance
- Benchmark skill performance with variance analysis

## Why a sidecar but no source

The plugin is managed by the official plugin marketplace. Copying it here would
duplicate what the marketplace already manages — see [[../hookify]],
[[../claude-md-management]], and [[../commit-commands]] for the same pattern.

The `.provenance.json` next to this README pins the upstream commit so this
repo's `SOURCES.md` still records that skill-creator is part of the user's setup.
