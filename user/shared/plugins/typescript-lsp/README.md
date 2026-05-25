# typescript-lsp (provenance-only)

This directory exists for provenance tracking only. The typescript-lsp plugin is **not** vendored here.

## What it does

TypeScript/JavaScript language server integration for Claude Code — provides go-to-definition, find references, and error checking for `.ts`, `.tsx`, `.js`, `.jsx`, `.mts`, `.cts`, `.mjs`, `.cjs` files.

## Prerequisites

```bash
npm install -g typescript-language-server typescript
```

## How it's actually installed

```
/plugin install typescript-lsp@claude-plugins-official
```

Run that slash command inside a Claude Code session. The plugin then lives at
`~/.claude/plugins/cache/claude-plugins-official/typescript-lsp/<version>/` and is
managed by Claude Code's plugin CLI.

## Where it's enabled

Project-scope only (not user-scope). Enabled in:
- `project-templates/nodejs/.claude/settings.json`
- `project-templates/nextjs/.claude/settings.json`
- `project-templates/phaser/.claude/settings.json`
