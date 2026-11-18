# user/shared/mcp/ — declared MCP servers

This directory records which Model Context Protocol (MCP) servers belong to the user-scope setup, **without** copying server source or storing any secrets. The actual server registration lives in `~/.claude.json` (or `~/.claude/mcp.json` on some setups), which is machine-local and out of scope. See the repo `README.md` § "Scope".

Mirrors the [`user/shared/plugins/`](../plugins/) pattern: one subdirectory per server, each containing a human-readable `README.md` and an optional `.provenance.json` sidecar when upstream git source exists.

## Where a server goes

A server reaches Claude Code in one of two ways. It is registered on the machine with `claude mcp add` and declared here, or it is added as a connector to the claude.ai account. The kind of server decides which (ADR 0125):

| Server | Where | Why |
|---|---|---|
| Runs locally (stdio) | `claude mcp add`, declared here | A connector needs a remote URL. |
| Remote, takes a secret in a header | `claude mcp add`, declared here | The secret stays in machine-local `~/.claude.json` and is listed in [`docs/SECRETS.md`](../../../docs/SECRETS.md). |
| Remote, signs in with OAuth | claude.ai connector, not declared here | One sign-in on the account covers every machine, the desktop app, and claude.ai chat. Signing in to Claude Code on a new machine brings the connector back. |

Register an OAuth server directly only when a connector can't do the job, such as a URL variant (a read-only endpoint) or a server one project needs (`--scope project` in that project). Claude Code then uses your entry and lists a connector with the same URL as hidden in `/mcp`.

Connectors load only while Claude Code signs in with a claude.ai subscription. A machine that uses an API key gets none of them. Some Anthropic-hosted connectors, such as Gmail and Google Calendar, can't be registered directly at all, because they don't support local OAuth from Claude Code.

## Layout

```
user/shared/mcp/
├── README.md                  # this file
└── <server-name>/
    ├── README.md              # registration command + what it provides
    └── .provenance.json       # only when upstream git source exists
```

## What goes in each `<server-name>/README.md`

- One-line description of what the server provides
- Transport (`http`, `sse`, `stdio`) and endpoint URL or command
- Scope (`user`, `project`, or `local`)
- Exact `claude mcp add ...` command with **placeholders for any secrets** (e.g., `<your-api-key>`, never the real value)
- Where to obtain credentials (dashboard URL) if applicable

Secrets — API keys, tokens, OAuth refresh tokens — must never appear here. They live only in the machine-local registration file.

## Adding a server

1. Create the directory and stub README:
   ```bash
   mkdir -p user/shared/mcp/<name>
   $EDITOR user/shared/mcp/<name>/README.md
   ```
2. If the server has a public upstream repo, pin a commit via provenance:
   ```bash
   bin/adopt --from <repo-url> \
             --path <path-in-repo>     # use '.' if the whole repo is the server \
             --to user/shared/mcp/<name> \
             --mode inspired-by \
             --license <SPDX>
   ```
   Omit `--commit` to pin upstream HEAD. For servers with no public source (hosted-only HTTP MCPs without a published repo), skip this step — the README alone is enough.
3. Register on this machine (or any new machine) by running the command from the new README. `install.sh` prints a reminder listing declared servers so you don't forget.

## Declared servers

Run `ls user/shared/mcp/` or check `SOURCES.md` for the current set. Canonical example: [`context7/`](context7/).
