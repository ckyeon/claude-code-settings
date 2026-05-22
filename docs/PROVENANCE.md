# Provenance Tracking — Schema & Conventions

This repo records the upstream origin of every adopted skill / agent / command / hook / template via JSON sidecar files. The system is **opt-in**: only items adopted from external sources need provenance metadata. Items you wrote yourself are implicitly "original" (no sidecar).

## Why a sidecar (not inline frontmatter)?

`SKILL.md`, agent and command definitions, and `CLAUDE.md` get loaded into Claude Code's context when invoked. Embedding provenance metadata in those files would waste context tokens on every invocation. Sidecar files live next to the content but never get loaded into the agent context.

## Schema

A sidecar `.provenance.json` file contains a single object with a `provenance` array:

```json
{
  "provenance": [
    {
      "source": "https://github.com/zircote/.claude",
      "commit": "a1b2c3d4e5f67890abcdef1234567890abcdef12",
      "path": "skills/foo/",
      "license": "MIT",
      "adopted-as": "copied",
      "adopted-at": "2026-05-21",
      "notes": "Stripped npm-specific examples"
    }
  ]
}
```

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | string | yes | Full URL of the upstream repository (`https://` or `git@`) |
| `commit` | string | yes | Full 40-character SHA of the source commit. Tags are not used (they can move). |
| `path` | string | yes | Path within the source repo to the adopted content |
| `license` | string | yes | SPDX identifier (e.g., `MIT`, `Apache-2.0`, `GPL-3.0`). Use `Unknown` if upstream doesn't declare one; `None` for public-domain. |
| `adopted-as` | string | yes | `copied` (content reproduced) or `inspired-by` (own implementation, design borrowed) |
| `adopted-at` | string | yes | ISO 8601 date (`YYYY-MM-DD`) when this entry was recorded |
| `notes` | string | optional | Free-form notes (what was changed, why) |

### `copied` vs `inspired-by`

| Mode | When to use |
|---|---|
| `copied` | You took upstream content largely as-is, with at most minor edits. |
| `inspired-by` | You wrote your own implementation, but the design idea or structure came from the source. |

When in doubt, prefer `inspired-by` — lower bar for attribution.

## Sidecar placement

| Item shape | Sidecar location |
|---|---|
| Folder (e.g., `user/shared/skills/foo/`, `project-templates/nodejs/`) | `<folder>/.provenance.json` (dot-prefixed, inside the folder) |
| Single file (e.g., `user/shared/commands/x.md`, `user/shared/hooks/y.sh`) | `<file>.provenance.json` (sibling in the same directory) |

Rationale: dot-prefixed `.provenance.json` inside a folder is hidden by default in `ls`, keeping folder listings clean. File-sibling naming makes the association obvious at a glance.

## Multi-source items

When an item draws from multiple upstream sources (combining ideas from several repos), append another entry to the `provenance` array. `bin/adopt` does this automatically when invoked again against the same destination.

```json
{
  "provenance": [
    { "source": "https://github.com/foo/a", "commit": "...", "path": "...", "license": "MIT", "adopted-as": "inspired-by", "adopted-at": "2026-05-15" },
    { "source": "https://github.com/bar/b", "commit": "...", "path": "...", "license": "Apache-2.0", "adopted-as": "copied",      "adopted-at": "2026-05-21" }
  ]
}
```

## Using `bin/adopt`

```bash
bin/adopt --from <repo-url> \
          --commit <sha-7-to-40> \
          --path <path-in-source-repo> \
          --to <local-destination> \
          --mode copied|inspired-by \
          --license <SPDX> \
          [--notes "..."]
```

What it does:
1. Validates arguments
2. Clones the upstream blobless and resolves the short SHA to a full 40-character SHA
3. For `copied` mode: sparse-checks-out and copies `<path>` to `<to>`
4. For `inspired-by` mode: skips the copy (your local implementation must already exist at `<to>`)
5. Writes or appends to the sidecar JSON
6. Prints a suggested `git commit` command (with trailers) — you run it yourself

`bin/adopt` never commits on your behalf. You control the commit boundary, including bundling unrelated edits.

## Using `bin/sources-index`

```bash
bin/sources-index
```

Walks the repo for every `*.provenance.json` file and rewrites `SOURCES.md` with two views:
- **By path** — every adopted item with source, commit, mode, license, date
- **By source** — same items grouped by upstream repo

Run it after every `adopt`, or as a pre-commit hook if you want full automation.

## Tracking officially-installed plugins

When a Claude Code plugin (with `.claude-plugin/plugin.json`) is installed via the official marketplace flow (`/plugin install <name>@<marketplace>`), the runtime artifact lives under `~/.claude/plugins/cache/<marketplace>/<name>/<version>/` and is managed by Claude Code's plugin CLI — not by this repo. To still record which upstream commit you're pinning to, use the **provenance-only** pattern:

1. Create `user/shared/plugins/<name>/` with a short `README.md` explaining that the directory exists for provenance only (no source vendored). The README satisfies `bin/adopt --mode inspired-by`'s "destination must exist" requirement.
2. Run `bin/adopt --mode inspired-by` against that directory with the upstream `--path plugins/<name>` and the commit SHA.

```bash
mkdir -p user/shared/plugins/<name>
$EDITOR user/shared/plugins/<name>/README.md   # see canonical examples below
bin/adopt --from <marketplace-repo-url> \
          --commit <sha> \
          --path plugins/<name> \
          --to user/shared/plugins/<name> \
          --mode inspired-by --license <SPDX>
```

This produces a sidecar with `adopted-as: "inspired-by"` and no source files. `bin/sources-index` lists the entry alongside `copied` ones; `install.sh` / `uninstall.sh` print plugin-name hints reminding you to run `/plugin install` (or `/plugin uninstall`) separately in a Claude Code session.

Canonical examples in this repo:
- `user/shared/plugins/hookify/` — plugin whose Python codebase cannot be split sensibly
- `user/shared/plugins/claude-md-management/` — plugin that's also `/plugin install`-able; provenance-only avoids duplicating what the marketplace already manages

When to prefer this over **split adoption** (copying skills/commands out of a plugin): use provenance-only whenever the plugin ships through a marketplace you've already added, or when the plugin has a `.claude-plugin/plugin.json` and you want Claude Code's official loader to handle activation. Use split adoption when you want only one artifact from a plugin and don't want the rest, or when the upstream isn't a marketplace plugin at all.

## Tracking MCP servers

Model Context Protocol (MCP) servers are registered per-machine via `claude mcp add ...` (or via claude.ai connector activation for hosted ones), and the registration — including any API-key headers — lives in machine-local `~/.claude.json` (or `~/.claude/mcp.json` on some setups). That file holds secrets and is **never** committed here. To still record which servers belong to the user-scope setup, use the **provenance-only** pattern, mirroring how plugins are tracked:

1. Create `user/shared/mcp/<name>/` with a `README.md` describing what the server provides and the exact `claude mcp add ...` registration command. Use placeholders (`<your-api-key>`) for any secret values — never paste real credentials.
2. If the server has a public upstream repo (the server source, not the hosted backend), pin a commit via `bin/adopt --mode inspired-by`:

```bash
mkdir -p user/shared/mcp/<name>
$EDITOR user/shared/mcp/<name>/README.md   # see canonical example below
bin/adopt --from <upstream-repo-url> \
          [--commit <sha>] \
          --path <path-in-repo>            # use '.' if the whole repo is the server \
          --to user/shared/mcp/<name> \
          --mode inspired-by --license <SPDX>
```

For servers with no public source (hosted-only HTTP MCPs without a published repo, claude.ai connectors), skip step 2 — the README alone is enough. `list_tracked_mcp_servers` in `lib/common.sh` enumerates everything under `user/shared/mcp/*/` that has a README, so sidecar presence is optional.

`install.sh` / `uninstall.sh` print MCP-name hints reminding you to run `claude mcp add` (or `claude mcp remove`) on each machine.

Canonical example:
- `user/shared/mcp/context7/` — hosted HTTP MCP server with an API-key header. README captures the registration command with `<your-api-key>` placeholder; the real key lives only in machine-local config.

## License compatibility

Each provenance entry records the upstream `license`. The auto-generated `SOURCES.md` provides a single browseable attribution list, which usually satisfies MIT / Apache-2.0 / BSD attribution requirements. For GPL-licensed sources, redistribution constraints apply — `SOURCES.md` is a starting point, not a substitute for license review.

## Edge cases

| Situation | What to do |
|---|---|
| Rename or move an adopted item | Move the sidecar along with it. Run `bin/sources-index` to refresh. |
| Delete an adopted item | Delete the sidecar too. Run `bin/sources-index`; the entry disappears from `SOURCES.md`. |
| Upstream has new commits since adoption | Currently manual. Re-run `bin/adopt` with the newer commit; the new entry is appended (older entry retained as history). |
| Adopted from a private repo | Same flow. The full SHA is recorded; viewers without access to the private repo can still see the metadata. |
| Tags only, no commit SHA available | Pick the commit the tag pointed to at the time. Tags can move; record the SHA, not the tag. |

## Files in this system

| Path | Role |
|---|---|
| `bin/adopt` | Adoption helper — record sources |
| `bin/sources-index` | Regenerate `SOURCES.md` |
| `lib/provenance.sh` | Shared helpers (used by both binaries) |
| `SOURCES.md` | Auto-generated index, committed alongside content |
| `docs/PROVENANCE.md` | This document |

## Dependencies

- `python3` (standard library only — no `pip install` needed)
- `git` (any modern version with `sparse-checkout` and `--filter=blob:none`)
- `bash` 3.2+ (macOS-default-compatible)
