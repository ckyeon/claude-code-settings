# hookify (provenance-only)

This directory exists for provenance tracking only. The hookify plugin is **not** vendored here.

## How it's actually installed

```
/plugin install hookify@claude-plugins-official
```

Run that slash command inside a Claude Code session. The plugin then lives at
`~/.claude/plugins/cache/claude-plugins-official/hookify/<version>/` and is
managed by Claude Code's plugin CLI (`~/.claude/plugins/installed_plugins.json`).

## Why a sidecar but no source

Hookify ships a Python codebase (`core/`, `matchers/`, `utils/`) plus hooks
that import those modules. Splitting it by artifact type the way
[[../claude-md-management]] was briefly tried would break it, and copying
the whole tree here would duplicate what the official plugin marketplace
already manages.

The `.provenance.json` next to this README pins the upstream commit so this
repo's `SOURCES.md` still records that hookify is part of the user's setup.
