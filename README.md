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
│   │   └── output-styles/      # → ~/.claude/output-styles
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

## What this repo deliberately does NOT manage

Claude Code creates and updates many files under `~/.claude/` at runtime. None of them are touched by this repo:

- `projects/` — per-project chat history (typically hundreds of MB)
- `plans/` — saved plans from sessions
- `sessions/`, `tasks/`, `shell-snapshots/`, `paste-cache/`, `image-cache/`, `file-history/` — caches and snapshots
- `history.jsonl`, `usage-data/`, `telemetry/`, `cache/` — telemetry/cache
- `credentials.json`, `mcp.json` — secrets (managed out-of-band per machine)
- `settings.local.json` — per-machine override
- `plugins/` — installed by Claude Code itself
