# fetch (declared)

This directory is a declaration. The fetch MCP server is **not** vendored here — its source lives at [github.com/modelcontextprotocol/servers/tree/main/src/fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch), distributed as the `mcp-server-fetch` Python package and run on-demand via `uvx`.

## What it provides

Retrieves content from web pages and converts HTML to markdown for easier LLM consumption. Useful when the model needs to read a documentation page, blog post, or any URL referenced in conversation.

## How it's actually registered

Stdio transport. Runtime is Python via `uvx` — install `uv` first (<https://docs.astral.sh/uv/getting-started/installation/>) if it isn't on `PATH`. No API key, no env vars required.

```bash
claude mcp add fetch --scope user -- uvx mcp-server-fetch
```

Verify:

```bash
claude mcp get fetch        # should show "Status: ✓ Connected"
```

To remove from this machine:

```bash
claude mcp remove fetch -s user
```

## Why a sidecar but no source

The server is published as a standalone package and runs as a transient `uvx` subprocess — vendoring source here wouldn't help reproduce the runtime. The `.provenance.json` next to this README pins the upstream commit so `SOURCES.md` records that `mcp-server-fetch` is part of the user's setup, and the README captures the registration command that does the actual work on each machine.
