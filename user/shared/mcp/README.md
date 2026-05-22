# user/shared/mcp/ — MCP server tracking (provenance-only)

This directory records which Model Context Protocol (MCP) servers belong to the user-scope setup, **without** copying server source or storing any secrets. The actual server registration lives in `~/.claude.json` (or `~/.claude/mcp.json` on some setups), which is machine-local and out-of-band by design — see the repo `README.md`'s "deliberately does NOT manage" list.

Mirrors the [`user/shared/plugins/`](../plugins/) pattern: one subdirectory per server, each containing a human-readable `README.md` and an optional `.provenance.json` sidecar when upstream git source exists.

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
   Omit `--commit` to pin upstream HEAD. For servers with no public source (claude.ai connectors, hosted-only HTTP MCPs without a published repo), skip this step — the README alone is enough.
3. Register on this machine (or any new machine) by running the command from the new README. `install.sh` prints a reminder listing tracked servers so you don't forget.

## Tracked servers

Run `ls user/shared/mcp/` or check `SOURCES.md` for the current set. Canonical example: [`context7/`](context7/).
