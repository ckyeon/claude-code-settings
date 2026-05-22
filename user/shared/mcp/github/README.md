# github (provenance-only)

This directory exists for provenance tracking only. The GitHub MCP server is **not** vendored here — its source lives at [github.com/github/github-mcp-server](https://github.com/github/github-mcp-server), and the hosted backend runs at `api.githubcopilot.com/mcp/`. Same hosted endpoint also has a Docker image (`ghcr.io/github/github-mcp-server`) for local stdio mode.

## What it provides

GitHub operations from inside Claude Code: repositories, issues, pull requests, code search, CI/CD checks, security alerts, releases, and more. Authoritative replacement for ad-hoc `gh` CLI shelling out.

## How it's actually registered

Two transports. **HTTP is recommended** (no Docker required, lower latency); stdio is the fallback when running entirely locally.

Both need a GitHub Personal Access Token. Get one at <https://github.com/settings/tokens> — fine-grained tokens are preferred, with whatever repository/issue scopes match your use case.

### HTTP (recommended)

```bash
claude mcp add \
  --transport http \
  --scope user \
  --header "Authorization=Bearer <your-github-pat>" \
  github https://api.githubcopilot.com/mcp/
```

### stdio (Docker)

```bash
claude mcp add \
  --scope user \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<your-github-pat> \
  -- github docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN \
  ghcr.io/github/github-mcp-server
```

### Verify

```bash
claude mcp get github        # should show "Status: ✓ Connected"
```

### Remove

```bash
claude mcp remove github -s user
```

## Relationship to the `github` plugin

The `claude-plugins-official` marketplace ships a `github` plugin that also auto-registers the same hosted backend (`api.githubcopilot.com/mcp/`) under the name `plugin:github:github`. This directory tracks the **direct-registration workflow** — registering the MCP server yourself without going through the plugin. Both registrations can coexist on one machine (different names → no collision), but typically you pick one path:

- **Direct registration** (this entry): full control over transport, headers, scope, and removal.
- **Plugin path**: install via `/plugin install github@claude-plugins-official`. Convenient bundle with other plugin features, but the MCP registration is owned by the plugin CLI.

If you want to track the plugin instead of (or in addition to) the direct workflow, create `user/shared/plugins/github/` following the [hookify](../../plugins/hookify/) / [claude-md-management](../../plugins/claude-md-management/) pattern. That's out of scope for this entry.

## Why a sidecar but no source

The server source is open (MIT) but Claude Code drives it as a remote HTTP service (or a Docker image when running stdio mode), so vendoring the source here wouldn't help reproduce the runtime. The `.provenance.json` pins the upstream commit so `SOURCES.md` records that github-mcp-server is part of the user's setup, and the README captures the registration command that does the actual work on each machine.

The PAT is a secret and lives only in machine-local `~/.claude.json` (or equivalent). It is never written into this repo.
