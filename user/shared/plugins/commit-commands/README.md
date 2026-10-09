# commit-commands (declared)

This directory is a declaration. The commit-commands plugin is **not** vendored here.

## How it's actually installed

```
/plugin install commit-commands@claude-plugins-official
```

Run that slash command inside a Claude Code session. The plugin then lives at
`~/.claude/plugins/cache/claude-plugins-official/commit-commands/<version>/` and is
managed by Claude Code's plugin CLI (`~/.claude/plugins/installed_plugins.json`).

## What the plugin ships

- Command `/commit` — stages changes and creates a commit with an auto-generated message matching repo style
- Command `/commit-push-pr` — commits, pushes, and creates a pull request in one step
- Command `/clean_gone` — removes local branches whose remote tracking branch is gone

## Why a sidecar but no source

The plugin is a set of command markdown files managed by the official plugin
marketplace. Copying them here would duplicate what the marketplace already
manages — see [[../hookify]] and [[../claude-md-management]] for the same pattern.

The `.provenance.json` next to this README pins the upstream commit so this
repo's `SOURCES.md` still records that commit-commands is part of the user's setup.
