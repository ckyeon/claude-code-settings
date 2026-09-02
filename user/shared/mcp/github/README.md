# github (provenance-only)

This directory exists for provenance tracking only. The GitHub MCP server is **not** vendored here — its source lives at [github.com/github/github-mcp-server](https://github.com/github/github-mcp-server), and the hosted backend runs at `api.githubcopilot.com/mcp/`. Same hosted endpoint also has a Docker image (`ghcr.io/github/github-mcp-server`) for local stdio mode.

## What it provides

GitHub operations from inside Claude Code: repositories, issues, pull requests, code search, CI/CD checks, security alerts, releases, and more. Authoritative replacement for ad-hoc `gh` CLI shelling out.

## PAT type and scopes

Verified against upstream `docs/scope-filtering.md` at the pinned commit (`12d16ed0`). Two token types behave differently with this server:

| Type | Prefix | Server behavior |
|---|---|---|
| **Classic PAT** | `ghp_` | Reads the token's OAuth scopes at startup (`X-OAuth-Scopes` header) and **hides tools** the token can't use |
| **Fine-grained PAT** | `github_pat_` | No scope detection — **all tools shown**; the GitHub API rejects calls the token lacks permission for |

Scopes to grant when issuing a **classic** token at <https://github.com/settings/tokens>:

- `repo` — the baseline; without it nearly every write tool is hidden (upstream's own troubleshooting starts with "verify PAT has `repo` scope"). Since upstream `198bc16`, a `public_repo`-only token still shows a handful of public-contribution write tools (issue comments, PR creation, fork/branch/push), but their per-call auth challenges still require full `repo`. Implicitly includes `public_repo` and `security_events`.
- `read:org` — org-level reads (e.g. listing an organization's issue fields/types).
- `workflow` — only needed when a file write touches `.github/workflows/`; the server requests it on top of `repo` just for those calls.
- `gist`, `notifications`, `project`, `admin:org` — only if you use the matching toolsets. Hierarchy: `admin:org` ⊃ `write:org` ⊃ `read:org`, and `project` ⊃ `read:project`.

Per-tool scope requirements are listed in the upstream [README's tools section](https://github.com/github/github-mcp-server#tools). Check what an existing token actually has:

```bash
curl -sI -H "Authorization: Bearer <your-github-pat>" \
  https://api.github.com/user | grep -i x-oauth-scopes
```

A **fine-grained** token trades tool filtering for tighter blast radius: select the specific repositories and grant the permission categories (Contents, Issues, Pull requests, ...) matching the tools you intend to use — mistakes surface as API errors at call time, not as hidden tools.

For everyday use here (repos, issues, PRs, CI), `repo` + `read:org` + `workflow` on a classic PAT is the practical minimum to start from.

## How it's actually registered

Two transports. **HTTP is recommended** (no Docker required, lower latency); stdio is the fallback when running entirely locally.

Both need a GitHub Personal Access Token — see the previous section for which type and which scopes to grant when issuing it.

### HTTP (recommended)

`--header` is variadic in the CLI, so it must come **after** the positional `<name>` and URL — otherwise it greedily consumes them and you get `missing required argument 'name'`. The header value uses HTTP-style `Key: value` (colon + space), not `Key=value`.

```bash
claude mcp add \
  --transport http \
  --scope user \
  github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer <your-github-pat>"
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
