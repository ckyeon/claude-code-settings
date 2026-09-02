# coding-agent-settings — Agent operations

This repo manages Claude Code settings across User and Project scopes, with provenance tracking for items adopted from external repos. Most changes happen through Claude Code / agent sessions — the conventions below codify what's converged on so far. Read these before making changes.

## Repo at a glance

- `user/{shared,mac,linux}/` — User-scope settings; symlinked into `~/.claude/` by `./install.sh`.
- `user/shared/plugins/` — Provenance-only for plugins installed via Claude Code's `/plugin install`. Not symlinked; see `docs/PROVENANCE.md` § "Tracking officially-installed plugins".
- `user/shared/mcp/` — Provenance-only for MCP servers registered via `claude mcp add`. Not symlinked; see `docs/PROVENANCE.md` § "Tracking MCP servers". Secrets (API keys) stay in machine-local `~/.claude.json` and never enter this repo.
- `.claude/skills/` — Project-scope skills (e.g., `check-updates`). Only active when working in this repo.
- `.claude/settings.json`, `.claude/hooks/` — Project-scope config. A `Stop` hook runs `bin/check-integrity` when a session here ends and asks Claude to fix any errors before stopping. Only active in this repo.
- `project-templates/{_base,nodejs,nextjs,python,go,phaser}/` — Templates copied into new projects via manual `cp -r` (no scaffold script).
- `bin/adopt`, `bin/sources-index`, `bin/check-updates` — Provenance tooling. JSON sidecars + auto-generated `SOURCES.md`.
- `bin/check-integrity` — Static validation. Catches items whose dependencies were never adopted; complements `check-updates` (freshness) with a function check.
- `docs/PROVENANCE.md` — Schema and edge cases for provenance.
- `docs/adr/` — Architecture Decision Records for this repo's own operational decisions.

## Workflows

### Adopt an external item

1. `bin/adopt --from <url> [--commit <sha>] --path <p> --to <dest> --mode copied|inspired-by --license <SPDX> [--notes "..."]`. Omitting `--commit` pins to upstream HEAD. Auto-runs `bin/sources-index` unless `--no-index`, then `bin/check-integrity` unless `--no-check`.
2. Review the diff and the new `.provenance.json` sidecar. **If the integrity check warned, resolve it before committing** — usually it means the item delegates to a skill you haven't adopted yet.
3. Commit using the printed `git commit ... --trailer ...` form (include `SOURCES.md`), or pass `--commit-now` to step 1 to skip the copy-paste.
4. Push only on explicit user request.

### Track an officially-installed plugin

Claude Code marketplace plugins (installed via `/plugin install <name>@<marketplace>`) are activated by the plugin CLI, not by this repo's symlinks. To record provenance:

1. `mkdir -p user/shared/plugins/<name> && $EDITOR user/shared/plugins/<name>/README.md`
2. `bin/adopt --from <marketplace-repo-url> --path plugins/<name> --to user/shared/plugins/<name> --mode inspired-by --license <SPDX>`

`/plugin install` updates `user/shared/settings.json` — include that file in the same commit. Those entries are load-bearing beyond activation: `install.sh` / `uninstall.sh` resolve each plugin's marketplace from `enabledPlugins` and each third-party marketplace's repo from `extraKnownMarketplaces` to print exact commands. A plugin tracked under `user/shared/plugins/` but missing from every `enabledPlugins` (user scope, or a project template's) prints as a warning instead of a usable command.

Third-party marketplaces must be registered per-machine with `/plugin marketplace add <owner>/<repo>` before `/plugin install` — `extraKnownMarketplaces` does not do it for you. Note the argument is the repo, not the marketplace name (`openai/codex-plugin-cc`, not `openai-codex`).

`install.sh` / `uninstall.sh` print `/plugin install` reminders listing tracked plugins. Canonical examples: `user/shared/plugins/hookify/`, `user/shared/plugins/claude-md-management/`, `user/shared/plugins/commit-commands/`, `user/shared/plugins/skill-creator/`.

### Track an MCP server

MCP servers are registered per-machine via `claude mcp add` and their config (including API-key headers) lives in machine-local `~/.claude.json` — secrets are never committed here. To track which servers belong to the user-scope setup:

1. `mkdir -p user/shared/mcp/<name> && $EDITOR user/shared/mcp/<name>/README.md`. The README must include the exact `claude mcp add ...` command with placeholder values for any secrets (e.g., `<your-api-key>`).
   - **Gotcha:** `--header` / `-e` are variadic — place them **after** `<name>` and `<commandOrUrl>` (or cap with `--`), or they'll greedily consume the positionals and emit `missing required argument 'name'`. Header values use HTTP-style `"Key: value"`, not `"Key=value"`.
2. (Optional, only if a public upstream repo exists) `bin/adopt --from <repo-url> --path <path> --to user/shared/mcp/<name> --mode inspired-by --license <SPDX>` — use `.` for `<path>` if the entire repo is the server (as with `context7`).

`install.sh` / `uninstall.sh` print `claude mcp add` / `claude mcp remove` reminders listing tracked servers. Canonical example: `user/shared/mcp/context7/`.

### Add a self-authored item

Just create the file or folder under `user/shared/{skills,commands,agents,hooks,rules,output-styles}/`. No sidecar — opt-in scope means "no provenance metadata" = "original work".

### Check for upstream updates

Run `bin/check-updates` or use the `/check-updates` skill in a Claude Code session. The script compares pinned commits against upstream HEAD; in `--deep` mode it also reports upstream entries added or removed next to tracked paths (new/deleted skills, with a warning when a removed entry is adopted here). The skill layers judgment on top: whether tracked paths actually changed, and what the structural changes mean.

### Check that adopted items still work

Run `bin/check-integrity` (add `--strict` to fail on warnings too). It is static, offline, and deterministic — no LLM, no network, no side effects — so it is safe to run on every change.

`check-updates` answers "is this pinned to the latest upstream?"; `check-integrity` answers "does this still function?". An item can be perfectly fresh and completely broken: `grill-with-docs` was re-synced four times while both skills it delegates to were absent (ADR 0020).

Two failure classes it catches:

- **Skill cross-references** — a `` `/name` `` written next to the noun "skill", or a quoted name near the phrase "Skill tool" (`call the Skill tool with "name"`), must resolve to an installed skill (this repo's `user/shared/skills/`, or one vendored in an installed plugin). Errors are high-precision; a second, softer pass warns on other unresolved `` `/token` `` refs.
- **Provenance sidecars** — valid JSON, non-empty `provenance[]`, required fields present. `"source": "self"` entries are exempt from `commit` / `path` / `license` (see `docs/PROVENANCE.md` § "Edge cases").

**When adopting an item, adopt what it delegates to.** Upstream categories don't always match: `grilling` lives under `skills/productivity/` while the skills that call it are in `skills/engineering/`, which is all the original adoption walked. `bin/adopt` now runs this check itself and warns before you commit (suppress with `--no-check`) — the rule is enforced by the tool, not by remembering it.

A warning mid-chain is expected: adopting the first of three dependencies leaves the other two unresolved. Finish the chain, then confirm `bin/check-integrity` is clean.

**Changes that never touch `bin/adopt`** — a hand-written skill, an edited `SKILL.md`, a deleted skill that others still reference — are covered by the project-scope `Stop` hook in `.claude/settings.json`. It runs the same check when a session here ends and blocks once, feeding the errors back so they get fixed while the session is still open. It stays silent when clean, and downgrades to a plain message if `stop_hook_active` is already set, so it cannot loop.

### Record a decision

Record an ADR in `docs/adr/` for **every** change to this repo — the user wants a complete history of decision records, not a selective log. When in doubt, write one. Scale the depth to the decision: a trivial change gets a one-line ADR, a consequential one gets the optional sections below.

Steps:

1. Pick the next sequential number: `docs/adr/NNNN-slug.md`.
2. Write a short title + 1-3 sentence summary (what was decided and why). Optional sections: Status, Considered Options, Consequences — only when they add genuine value.
3. Commit with the change it documents.

### Update an adoption to a newer upstream commit

Re-run `bin/adopt` against the same destination with the new SHA. The sidecar's `provenance[]` list gets a new entry appended; the older entry stays as history. `bin/adopt` compares the old and new pins itself and warns when upstream added or removed entries next to the path (new/deleted sibling skills), or when an `inspired-by` path no longer exists at the new commit — so a hand-run re-pin gets the same structural check as `check-updates --deep` (ADR 0039).

## Guardrails

- **No auto-commit.** Wait for an explicit commit request from the user.
- **`./install.sh` needs explicit confirmation.** It backs up existing `~/.claude/` content (including `skills/`, which the user has many of) before symlinking. Always explain the impact and confirm before running.
- **No `git config` changes** through tooling — including `--set-upstream`. The user manages remote configuration themselves.
- **No `git push` without an explicit request.**
- **Dependencies stay minimal**: Python 3 stdlib + bash 3.2 only. Don't introduce `yq`, `PyYAML`, `jq`, or other external deps.
- **Provenance lives in sidecars only.** Never inline in `SKILL.md` / agent / command / `CLAUDE.md` frontmatter — those files load into Claude's context when invoked, so embedded metadata becomes context noise.
- **Two `plugins/` directories — don't confuse them.** `~/.claude/plugins/` is Claude Code's own plugin CLI state (registry, marketplaces, cache); never symlinked from here. `user/shared/plugins/` in this repo is provenance-only — no source vendored; activation is via `/plugin install`.
- **MCP secrets stay machine-local.** `user/shared/mcp/<name>/README.md` may contain registration commands but must use placeholders (`<your-api-key>`) for any secret values. The real `~/.claude.json` / `~/.claude/mcp.json` is on the "deliberately does NOT manage" list.

## References

- [`README.md`](README.md) — install workflow, scope model, OS handling
- [`docs/PROVENANCE.md`](docs/PROVENANCE.md) — provenance schema, conventions, edge cases
- [`docs/adr/`](docs/adr/) — decision records
- `bin/adopt --help` — adoption CLI reference
