# context7 (provenance-only)

This directory exists for provenance tracking only. The context7 MCP server is **not** vendored here — it's a hosted HTTP MCP server operated by Upstash. The upstream repo at [github.com/upstash/context7](https://github.com/upstash/context7) contains the server source.

## What it provides

Up-to-date, version-specific library documentation and code examples on demand. Reduces hallucinated APIs by fetching real docs at query time instead of relying on training-data recall.

## How it's actually registered

Hosted at `https://mcp.context7.com/mcp` (HTTP transport). Requires a free API key from [context7.com/dashboard](https://context7.com/dashboard).

```bash
claude mcp add \
  --transport http \
  --scope user \
  --header "CONTEXT7_API_KEY=<your-api-key>" \
  context7 https://mcp.context7.com/mcp
```

Verify:

```bash
claude mcp get context7        # should show "Status: ✓ Connected"
```

To remove from this machine:

```bash
claude mcp remove context7 -s user
```

## Why a sidecar but no source

The server runs as a hosted service — copying source here wouldn't help reproduce the runtime. The `.provenance.json` next to this README pins the upstream commit so this repo's `SOURCES.md` records that context7 is part of the user's setup, and the README captures the registration command that does the actual work on each machine.

The `CONTEXT7_API_KEY` header value is a secret and lives only in machine-local `~/.claude.json` (or equivalent). It is never written into this repo.
