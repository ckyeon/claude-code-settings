# linear (provenance-only, README-only)

This directory exists for tracking only. The Linear MCP server is **not** vendored here — it's a hosted HTTP MCP server operated by Linear at `mcp.linear.app`, and Linear does not publish its source. There is therefore no `.provenance.json` sidecar (nothing to pin); this README is the whole record. See [`../README.md`](../README.md) § "Adding a server", step 2.

Official docs: <https://linear.app/docs/mcp>.

## What it provides

Find, create, and update Linear objects — issues, projects, comments, and related workspace data — from inside Claude Code, so the agent can read and act on the issue tracker instead of being pasted ticket text.

## How it's actually registered

Hosted at `https://mcp.linear.app/mcp` (Streamable HTTP). `https://mcp.linear.app/sse` still works but is a deprecated fallback — don't use it for new registrations.

Authentication is **OAuth 2.1 with dynamic client registration** — no API key is needed. `claude mcp add` only records the server; the browser sign-in happens afterwards from `/mcp` inside a Claude Code session.

The server name here is `linear` (short names, matching the sibling entries); Linear's docs use `linear-server`. Either works — the name only determines the tool prefix (`mcp__linear__*`).

```bash
claude mcp add \
  --transport http \
  --scope user \
  linear https://mcp.linear.app/mcp
```

Then, in a Claude Code session:

```
/mcp    →  select "linear"  →  Authenticate   (opens the browser)
```

### Read-only variant

Swap the URL for `https://mcp.linear.app/mcp/readonly` to get a token that cannot reach Linear's write APIs — useful when the agent should only look things up.

```bash
claude mcp add --transport http --scope user linear https://mcp.linear.app/mcp/readonly
```

### Non-interactive alternative (API key as bearer)

Only for headless setups where the OAuth flow is impractical. `--header` is variadic, so it must come **after** the positional `<name>` and URL, and the value is HTTP-style `Key: value`.

```bash
claude mcp add \
  --transport http \
  --scope user \
  linear https://mcp.linear.app/mcp \
  --header "Authorization: Bearer <your-linear-api-key>"
```

Get a key at Linear → Settings → Security & access → Personal API keys. The key is a secret and lives only in machine-local `~/.claude.json`; never write the real value into this repo.

### Verify

```bash
claude mcp get linear        # "Needs authentication" until /mcp sign-in, then "✓ Connected"
```

### Remove

```bash
claude mcp remove linear -s user
```

## Relationship to the `claude.ai Linear` connector

Accounts with the Linear connector enabled on claude.ai also see it in Claude Code as `claude.ai Linear` (scope: "claude.ai config"), pointing at the **same** `https://mcp.linear.app/mcp`. That entry follows the account, not this repo — it can't be registered or removed from here.

This directory tracks the **direct-registration workflow**. Both can coexist (different names → no collision), but authenticating both loads two copies of every Linear tool into context (`mcp__linear__*` and `mcp__claude_ai_Linear__*`). Pick one:

- **Direct registration** (this entry): reproducible from this repo via `install.sh`'s reminder; full control over transport, URL variant, scope, and removal.
- **claude.ai connector**: zero config wherever you log in, but outside this repo's control.

If you use this entry, leave `claude.ai Linear` unauthenticated (or disable it from `/mcp`).

## Why no sidecar

`.provenance.json` pins an upstream git commit so `bin/check-updates` can report drift. Linear's server has no public repo to pin, so there is nothing for the sidecar to say — and nothing for `check-updates` or `SOURCES.md` to track. This README is the record; `install.sh` / `uninstall.sh` list the server from the directory name alone.

OAuth tokens issued during `/mcp` sign-in are stored machine-locally by Claude Code and never enter this repo.
