# understand-anything (provenance-only)

This directory exists for provenance tracking only. The understand-anything plugin is **not**
vendored here.

## How it's actually installed

```
/plugin marketplace add Lum1104/Understand-Anything
/plugin install understand-anything
/reload-plugins
```

Run those slash commands inside a Claude Code session. Like [[../codex]], this ships from a
**third-party marketplace** (`understand-anything`, published by Lum1104), so the
`/plugin marketplace add` step is required first — it records the marketplace under
`extraKnownMarketplaces` in `user/shared/settings.json`. The plugin then lives under
`~/.claude/plugins/cache/understand-anything/understand-anything/<version>/` and is managed by
Claude Code's plugin CLI (`~/.claude/plugins/installed_plugins.json`).

No API key is required — the plugin analyzes local code within the session. It bundles a TypeScript
pnpm-workspace runtime (`src/`, `packages/`), so Node is needed wherever that runtime executes.

## What the plugin ships

- Command `/understand` — multi-agent pipeline that scans the project (files, functions, classes,
  dependencies) and builds a knowledge graph at `.understand-anything/knowledge-graph.json`
- Command `/understand-dashboard` — opens an interactive web dashboard visualizing the codebase as a
  searchable, layer-colored graph
- Bundled agents, hooks, and skills plus a TS runtime — see upstream for source

## Why a sidecar but no source

The plugin is managed by its marketplace; copying it here would duplicate what the marketplace
already manages — see [[../codex]], [[../hookify]], [[../claude-md-management]],
[[../commit-commands]], and [[../skill-creator]] for the same pattern. It also ships a
Node/TypeScript runtime that can't be split sensibly, the same reason [[../hookify]] is tracked
whole.

This is the second tracked plugin from a non-Anthropic marketplace (after [[../codex]]). The
`.provenance.json` next to this README pins the upstream commit so this repo's `SOURCES.md` still
records that understand-anything is part of the user's setup.
