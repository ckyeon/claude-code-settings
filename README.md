# coding-agent-settings

Personal Claude Code settings, version-controlled across **scopes** (User / Project) and **OSes** (macOS / Linux).

## Quick start

```bash
git clone <this-repo> ~/workspace/toy-project/coding-agent-settings
cd ~/workspace/toy-project/coding-agent-settings
./install.sh
```

Existing `~/.claude/CLAUDE.md`, `settings.json`, etc. (if any) are moved to `*.backup-<timestamp>` before being replaced. Re-running `./install.sh` is safe and idempotent.

## Scope model

Claude Code has three scopes. This repo manages two of them:

| Scope | Lives in | Managed here? |
|---|---|---|
| **User** (global) | `~/.claude/` | yes — symlinked from `user/` |
| **Project** (per-repo, committed) | `<project>/.claude/`, `<project>/CLAUDE.md` | yes — as templates in `project-templates/` |
| **Local** (per-machine, gitignored) | `<project>/.claude/settings.local.json` | no — machine-local by design |

## OS handling

OS-specific files live under `user/mac/` or `user/linux/`. `install.sh` detects the OS with `uname -s` and only symlinks the matching one.

- `user/shared/` — everything that's the same on every machine
- `user/mac/` — macOS-only (statusline, hooks that need `osascript`, `pbcopy`, etc.)
- `user/linux/` — Linux-only (statusline, hooks that need `xclip`, `notify-send`, etc.)

`settings.json` references hook paths through a fixed layout (`~/.claude/hooks/shared/<name>`, `~/.claude/hooks/os/<name>`), so it stays OS-agnostic.

## Repo layout

```
.
├── install.sh                  # idempotent OS-aware installer
├── uninstall.sh                # remove our symlinks, restore .backup-*
├── lib/common.sh               # shared bash helpers
├── user/                       # → ~/.claude/
│   ├── shared/                 # OS-agnostic
│   │   ├── CLAUDE.md
│   │   ├── settings.json
│   │   ├── skills/             # → ~/.claude/skills
│   │   ├── commands/           # → ~/.claude/commands
│   │   ├── agents/             # → ~/.claude/agents
│   │   ├── hooks/              # → ~/.claude/hooks/shared
│   │   ├── rules/              # → ~/.claude/rules
│   │   ├── output-styles/      # → ~/.claude/output-styles
│   │   ├── plugins/            # provenance-only (not symlinked; see Provenance / Sources)
│   │   └── mcp/                # provenance-only MCP server tracking (not symlinked)
│   ├── mac/
│   │   ├── statusline-command.sh
│   │   └── hooks/              # → ~/.claude/hooks/os (when on Mac)
│   └── linux/
│       ├── statusline-command.sh
│       └── hooks/              # → ~/.claude/hooks/os (when on Linux)
└── project-templates/          # copy these into new projects
    ├── _base/                  # shared by every template
    ├── nodejs/
    ├── python/
    └── go/
```

## Adding a skill

Skills are folders containing a `SKILL.md`:

```bash
mkdir -p user/shared/skills/my-skill
$EDITOR user/shared/skills/my-skill/SKILL.md
git add user/shared/skills/my-skill
git commit -m "Add my-skill"
```

The next `claude` session picks it up — no re-install needed (the symlink is live).

## Adding an OS-specific hook

```bash
$EDITOR user/mac/hooks/notify.sh    # macOS-only
$EDITOR user/linux/hooks/notify.sh  # Linux-only
chmod +x user/{mac,linux}/hooks/notify.sh
git add user/{mac,linux}/hooks/notify.sh
git commit -m "Add notify hook"
```

Reference from `user/shared/settings.json` as `~/.claude/hooks/os/notify.sh` — the OS-specific symlink dispatches to the right file.

## Using a project template

In a new project directory:

```bash
TEMPLATES=~/workspace/toy-project/coding-agent-settings/project-templates
cp -r "$TEMPLATES/_base/." .
cp -r "$TEMPLATES/nodejs/." .                  # pick one: nodejs / python / go
cat "$TEMPLATES/_base/.gitignore.snippet" >> .gitignore
$EDITOR CLAUDE.md                              # replace {{PROJECT_NAME}}, fill in details
git add CLAUDE.md .claude .gitignore
```

Claude Code creates `.claude/settings.local.json` on demand — it's already gitignored.

## Multi-machine workflow

On a second machine:

```bash
git clone <this-repo> ~/workspace/toy-project/coding-agent-settings
cd ~/workspace/toy-project/coding-agent-settings
./install.sh   # auto-detects OS, picks user/{mac,linux} accordingly
```

For ongoing updates: `git pull && ./install.sh` (idempotent — only re-links what changed).

## Uninstall

```bash
./uninstall.sh
```

Removes only the symlinks that point into this repo. If `install.sh` previously made backups (`*.backup-<timestamp>`), the most recent one for each removed symlink is restored.

## Troubleshooting

- **Broken symlink in `~/.claude/`** — the repo was moved or deleted. Move it back, or run `./uninstall.sh` (it's a no-op if the symlink targets are gone) and re-clone.
- **`settings.json` not loading** — check `readlink ~/.claude/settings.json` resolves into this repo, then validate JSON with `python3 -m json.tool < ~/.claude/settings.json`.
- **Statusline missing** — `chmod +x user/{mac,linux}/statusline-command.sh` and re-run `./install.sh`.

## Provenance / Sources

When you adopt a skill, command, hook, or template from another public repo, record the source so you don't lose track of where it came from. The system uses JSON sidecar files (`.provenance.json`) so the metadata never lands in Claude Code's context.

Quick example:

```bash
bin/adopt --from https://github.com/example/dotfiles \
          --commit a1b2c3d4 \
          --path skills/notify \
          --to user/shared/skills/notify \
          --mode copied \
          --license MIT
```

This copies the upstream content, writes `user/shared/skills/notify/.provenance.json`, and prints a `git commit` command for you to run. The repo-level `SOURCES.md` is a browseable index — regenerate it after adopting with `bin/sources-index`.

See [`docs/PROVENANCE.md`](docs/PROVENANCE.md) for the schema, conventions, and edge cases. The tooling uses Python 3 standard library only (no external dependencies required).

### Adopting a Claude Code plugin

Plugins from a marketplace repo (e.g., `anthropics/claude-plugins-official`) ship a `.claude-plugin/plugin.json` and often bundle skills + commands + agents + Python hooks together. There are two adoption patterns depending on whether you want to vendor source or just track that the plugin is part of your setup.

**Split adoption** — extract individual artifacts. Use when the upstream plugin's pieces are independent and you want them activated through this repo's existing user-scope symlinks (`~/.claude/skills/`, `~/.claude/commands/`, …).

```bash
bin/adopt --from https://github.com/anthropics/claude-plugins-official.git \
          --commit <sha> \
          --path plugins/<plugin>/skills/<skill> \
          --to user/shared/skills/<skill> \
          --mode copied --license Apache-2.0
```

**Provenance-only** — record the upstream pin, but don't copy any source. Use when you've installed the plugin via Claude Code's official `/plugin install <name>@<marketplace>` and just want this repo to remember which commit was active.

```bash
mkdir -p user/shared/plugins/<plugin> && echo "# <plugin> (provenance-only)" > user/shared/plugins/<plugin>/README.md
bin/adopt --from https://github.com/anthropics/claude-plugins-official.git \
          --commit <sha> \
          --path plugins/<plugin> \
          --to user/shared/plugins/<plugin> \
          --mode inspired-by --license Apache-2.0
```

The provenance-only directory is **not** symlinked into `~/.claude/plugins/` — that path is owned by Claude Code's plugin CLI. `install.sh` and `uninstall.sh` print reminders listing tracked plugins so you don't forget the `/plugin install` step on a fresh machine. See `user/shared/plugins/hookify/` and `user/shared/plugins/claude-md-management/` for canonical examples.

### Tracking an MCP server

MCP servers are registered per-machine via `claude mcp add` (or claude.ai connector activation). The registration — including API-key headers — lives in machine-local `~/.claude.json` and is a secret-bearing file, so it stays out of this repo. To record which servers belong to the user-scope setup without leaking secrets, use the same provenance-only pattern as plugins:

```bash
mkdir -p user/shared/mcp/<name>
$EDITOR user/shared/mcp/<name>/README.md   # registration command with <your-api-key> placeholders
# Optional: pin the upstream server source if a public repo exists
bin/adopt --from <upstream-repo-url> \
          --path <path-or-.> \
          --to user/shared/mcp/<name> \
          --mode inspired-by --license <SPDX>
```

`install.sh` / `uninstall.sh` print MCP-name reminders listing tracked servers. See `user/shared/mcp/context7/` for the canonical example (hosted HTTP MCP with an API-key header). Full schema and conventions: [`docs/PROVENANCE.md`](docs/PROVENANCE.md) § "Tracking MCP servers".

## What this repo deliberately does NOT manage

Claude Code creates and updates many files under `~/.claude/` at runtime. None of them are touched by this repo:

- `projects/` — per-project chat history (typically hundreds of MB)
- `plans/` — saved plans from sessions
- `sessions/`, `tasks/`, `shell-snapshots/`, `paste-cache/`, `image-cache/`, `file-history/` — caches and snapshots
- `history.jsonl`, `usage-data/`, `telemetry/`, `cache/` — telemetry/cache
- `credentials.json`, `mcp.json` — secrets (managed out-of-band per machine). The non-secret half of MCP server inventory is tracked separately in `user/shared/mcp/`; see Provenance / Sources § "Tracking an MCP server".
- `settings.local.json` — per-machine override
- `~/.claude/plugins/` — Claude Code's own plugin CLI state (marketplaces, installed-plugin registry, cache). Distinct from `user/shared/plugins/` in this repo, which only tracks provenance for plugins you've installed via `/plugin install` (see Provenance / Sources).
