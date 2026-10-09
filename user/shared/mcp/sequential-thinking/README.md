# sequential-thinking (declared)

This directory is a declaration. The sequential-thinking MCP server is **not** vendored here — its source lives at [github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking), distributed as the `@modelcontextprotocol/server-sequential-thinking` npm package and run on-demand via `npx`.

## What it provides

A `sequential_thinking` tool that structures multi-step reasoning into an explicit chain of thoughts, with support for revising earlier steps and branching alternative paths. Useful for complex planning or analysis tasks where the model benefits from making its reasoning explicit.

## How it's actually registered

Stdio transport. Runtime is Node via `npx` — install Node.js (<https://nodejs.org/>) if it isn't on `PATH`. No API key, no env vars required.

```bash
claude mcp add sequential-thinking --scope user -- npx -y @modelcontextprotocol/server-sequential-thinking
```

Verify:

```bash
claude mcp get sequential-thinking        # should show "Status: ✓ Connected"
```

To remove from this machine:

```bash
claude mcp remove sequential-thinking -s user
```

## Why a sidecar but no source

The server is published as a standalone npm package and runs as a transient `npx` subprocess — vendoring source here wouldn't help reproduce the runtime. The `.provenance.json` next to this README pins the upstream commit so `SOURCES.md` records that `@modelcontextprotocol/server-sequential-thinking` is part of the user's setup, and the README captures the registration command that does the actual work on each machine.
