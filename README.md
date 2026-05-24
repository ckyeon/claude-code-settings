# coding-agent-settings

Personal Claude Code settings, version-controlled across **scopes** (User / Project) and **OSes** (macOS / Linux). Clone once, symlink everywhere.

## Quick start

**Prerequisites:** Bash 4.0+, macOS or Linux.

```bash
git clone <this-repo>
cd coding-agent-settings
./install.sh
```

The installer detects your OS, symlinks user-scope files into `~/.claude/`, and prints what it did:

```
Installing Claude Code user-scope settings symlinks...
  REPO_ROOT:  /path/to/coding-agent-settings
  CLAUDE_DIR: /Users/you/.claude
  OS:         mac

Done: 10 created, 0 backed up, 0 already linked.
```

If a file already exists at a symlink target, it is backed up as `<name>.backup-YYYYMMDD-HHMMSS` before being replaced. Re-running `./install.sh` is safe and idempotent — already-correct symlinks are skipped.

Verify with:

```bash
readlink ~/.claude/settings.json   # should point into this repo
```

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
├── CLAUDE.md                   # project-scope agent instructions (for this repo)
├── SOURCES.md                  # auto-generated provenance index
├── lib/common.sh               # shared bash helpers
├── bin/
│   ├── adopt                   # adopt items from external repos
│   ├── sources-index           # regenerate SOURCES.md
│   └── check-updates           # compare pins against upstream HEAD
├── docs/
│   └── PROVENANCE.md           # provenance schema & conventions
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
│   │   ├── plugins/            # provenance-only (not symlinked; see Provenance)
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
    ├── go/
    └── phaser/
```

## Multi-machine workflow

On a second machine:

```bash
git clone <this-repo>
cd coding-agent-settings
./install.sh   # auto-detects OS, picks user/{mac,linux} accordingly
```

For ongoing updates: `git pull && ./install.sh` (idempotent — only re-links what changed).

## Customization

### Adding a skill

Skills are folders containing a `SKILL.md`:

```bash
mkdir -p user/shared/skills/my-skill
$EDITOR user/shared/skills/my-skill/SKILL.md
git add user/shared/skills/my-skill
git commit -m "Add my-skill"
```

The next `claude` session picks it up — no re-install needed (the symlink is live).

### Adding an OS-specific hook

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
TEMPLATES=<path-to-coding-agent-settings>/project-templates
cp -r "$TEMPLATES/_base/." .
cp -r "$TEMPLATES/nodejs/." .                  # pick one: nodejs / python / go / phaser
cat "$TEMPLATES/_base/.gitignore.snippet" >> .gitignore
$EDITOR CLAUDE.md                              # replace {{PROJECT_NAME}}, fill in details
git add CLAUDE.md .claude .gitignore
```

The language-specific `CLAUDE.md` **replaces** the base version (not merged). If you need content from both, merge manually after copying.

Claude Code creates `.claude/settings.local.json` on demand — it's already gitignored.

## Provenance / Sources

When you adopt a skill, command, hook, or template from another public repo, `bin/adopt` records the source in a JSON sidecar (`.provenance.json`):

```bash
bin/adopt --from https://github.com/example/dotfiles \
          --commit a1b2c3d4 \
          --path skills/notify \
          --to user/shared/skills/notify \
          --mode copied \
          --license MIT
```

This copies the upstream content, writes the sidecar, and prints a `git commit` command. `SOURCES.md` is a browsable index — regenerate with `bin/sources-index`.

For the full schema, plugin/MCP adoption workflows, and edge cases, see [`docs/PROVENANCE.md`](docs/PROVENANCE.md).

## Uninstall

```bash
./uninstall.sh
```

Removes only the symlinks that point into this repo. If `install.sh` previously made backups, the most recent `.backup-*` for each removed symlink is restored automatically.

## Troubleshooting

- **Broken symlink in `~/.claude/`** — the repo was moved or deleted. Move it back, or run `./uninstall.sh` (it's a no-op if the symlink targets are gone) and re-clone.
- **`settings.json` not loading** — check `readlink ~/.claude/settings.json` resolves into this repo, then validate JSON with `python3 -m json.tool < ~/.claude/settings.json`.
- **Statusline missing** — `chmod +x user/{mac,linux}/statusline-command.sh` and re-run `./install.sh`.

## What this repo deliberately does NOT manage

Claude Code creates and updates many files under `~/.claude/` at runtime. None of them are touched by this repo:

- **History & caches** — `projects/`, `plans/`, `sessions/`, `tasks/`, `shell-snapshots/`, `paste-cache/`, `image-cache/`, `file-history/`, `history.jsonl`, `usage-data/`, `telemetry/`, `cache/`
- **Secrets** — `credentials.json`, `mcp.json` (managed out-of-band per machine; non-secret MCP inventory tracked separately in `user/shared/mcp/`)
- **Runtime state** — `settings.local.json` (per-machine override), `~/.claude/plugins/` (Claude Code's own plugin CLI state, distinct from `user/shared/plugins/` which only tracks provenance)
