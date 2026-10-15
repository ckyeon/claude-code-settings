# coding-agent-settings

Personal Claude Code settings, version-controlled across **scopes** (User / Project) and **OSes** (macOS / Linux). Clone once, symlink everywhere.

The goal is **reproduction**: a new machine reaches the same Claude Code environment from this repo and its docs alone.

## Quick start

These steps reproduce the setup on a new machine. **Prerequisites:** Bash 3.2+, Python 3, macOS or Linux.

1. **Link the owned files.**

   ```bash
   git clone <this-repo>
   cd coding-agent-settings
   ./install.sh
   ```

   The installer detects your OS and symlinks the owned files into `~/.claude/`. A file already at a symlink target is backed up as `<name>.backup-YYYYMMDD-HHMMSS` first. Re-running is safe: correct symlinks are skipped.

2. **Sign in.** Start `claude` and sign in. The skills, plugins, and connectors synced from claude.ai arrive with the account.

3. **Install the declared plugins.** `install.sh` printed one `/plugin marketplace add` or `/plugin install` line per plugin. Run them inside a Claude Code session.

4. **Register the declared MCP servers.** For each name `install.sh` listed, run the `claude mcp add` command in `user/shared/mcp/<name>/README.md`.

5. **Enter the secrets.** [`docs/SECRETS.md`](docs/SECRETS.md) lists each one and where it goes. Steps 3 and 4 ask for some of them as you go.

6. **Confirm.**

   ```bash
   bin/check-machine
   ```

   Reproduction is complete when it reports no errors. It checks the symlinks, the plugins enabled at user scope, and the MCP registrations. It does not check secrets.

To pick up later changes on a machine that is already set up: `git pull && ./install.sh`.

## Scope

This repo covers Claude Code only. Every item sits at one of three levels, defined in [`GLOSSARY.md`](GLOSSARY.md):

- **Owned**: the file in this repo is the setting that applies. `install.sh` symlinks it into `~/.claude/`.
- **Declared**: this repo lists the item and the command that creates it. You run that command on each machine.
- **Out of scope**: this repo neither stores nor checks it.

This section is the single list of what sits at which level. The rule for classifying something new is in [`CLAUDE.md`](CLAUDE.md) § "Scope".

| Item | Level | In this repo | Reaches a machine by |
|---|---|---|---|
| Global instructions | owned | `user/shared/CLAUDE.md` | symlink |
| Settings | owned | `user/shared/settings.json` | symlink |
| Skills, commands, agents, rules, output styles | owned | `user/shared/<kind>/` | symlink |
| Hooks | owned | `user/shared/hooks/`, `user/<os>/hooks/` | symlink |
| Status line scripts | owned | `user/<os>/` | symlink |
| Project templates | owned | `project-templates/` | manual copy into a new project |
| This repo's own project config | owned | `.claude/`, `CLAUDE.md` | cloning the repo |
| Plugins | declared | `user/shared/plugins/<name>/`, `enabledPlugins` in `settings.json` | `/plugin install` |
| MCP servers | declared | `user/shared/mcp/<name>/README.md` | `claude mcp add` |
| Secret names and where each goes | declared | [`docs/SECRETS.md`](docs/SECRETS.md) | entering each value by hand |

No keybindings file exists yet. Once one is created it is owned, and it joins `list_owned_links` in `lib/common.sh`.

Out of scope:

- **Installed plugin versions.** The plugin CLI updates them on its own schedule. A sidecar pin records the upstream point last reviewed, not the version installed.
- **Secret values.** They are entered per machine and never committed.
- **`~/.claude.json`.** It holds MCP registrations with their keys and per-project state.
- **Memory** (`~/.claude/projects/*/memory/`). It is per-machine working state. A lesson that must survive a machine change belongs in an owned file such as `CLAUDE.md` or a rule.
- **Discord access policy** (`~/.claude/channels/`). The discord plugin's own skill writes it, and access is granted again on each machine.
- **History, caches, sessions, telemetry**, and the plugin CLI's state under `~/.claude/plugins/`.
- **Skills, plugins, and connectors synced from claude.ai**, plus Claude in Chrome and computer use. They follow the account on sign-in.
- **Each project's own `.claude/` and `CLAUDE.md`**, including a project copied from a template. That project's repo owns them.
- **`settings.local.json`.** It is the per-machine override by design.
- **Codex configuration.**

## OS handling

OS-specific files live under `user/mac/` or `user/linux/`. `install.sh` detects the OS with `uname -s` and only symlinks the matching one. The Linux side has not been verified on a real machine yet.

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
├── GLOSSARY.md                 # terms: reproduce, owned, declared, out of scope
├── SOURCES.md                  # auto-generated provenance index
├── lib/                        # common.sh for the bash scripts, *.py modules the tools import
├── bin/
│   ├── adopt                   # adopt items from external repos
│   ├── re-pin                  # move the pin of items already adopted
│   ├── sources-index           # regenerate SOURCES.md
│   ├── check-updates           # compare pins against upstream HEAD
│   ├── check-integrity         # static checks: refs resolve, sidecars valid, declarations complete
│   └── check-machine           # does this machine match what the repo owns and declares?
├── tests/run.sh                # tests for the bin/ tools (fake upstream, temp dir)
├── evals/                      # do the user settings still change behavior on a given model?
├── docs/
│   ├── PROVENANCE.md           # provenance schema & conventions
│   └── SECRETS.md              # which secrets the setup needs and where each goes
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
│   │   ├── plugins/            # declared plugins (not symlinked; see Scope)
│   │   └── mcp/                # declared MCP servers (not symlinked; see Scope)
│   ├── mac/
│   │   ├── statusline-command.sh
│   │   ├── subagent-statusline.sh
│   │   └── hooks/              # → ~/.claude/hooks/os (when on Mac)
│   └── linux/
│       ├── statusline-command.sh
│       ├── subagent-statusline.sh
│       └── hooks/              # → ~/.claude/hooks/os (when on Linux)
└── project-templates/          # copy these into new projects
    ├── _base/                  # shared by every template
    ├── nodejs/
    ├── nextjs/
    ├── python/
    ├── go/
    ├── phaser/
    ├── video/
    └── cpp/
```

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
cp -r "$TEMPLATES/nodejs/." .                  # pick one: nodejs / nextjs / python / go / phaser / video / cpp
cat "$TEMPLATES/_base/.gitignore.snippet" >> .gitignore   # video: append video/.gitignore.snippet instead (media files)
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

This copies the upstream content, writes the sidecar, and prints a `git commit` command. `SOURCES.md` is a browsable index — regenerate with `bin/sources-index`. To move an adopted item to a newer upstream commit later, run `bin/re-pin <local-path>`.

For the full schema, plugin/MCP adoption workflows, and edge cases, see [`docs/PROVENANCE.md`](docs/PROVENANCE.md).

### Checking adopted items

Two checks answer different questions:

```bash
bin/check-updates      # is the pin behind upstream HEAD?
bin/check-integrity    # do cross-references resolve, sidecars validate, declarations carry their commands?
```

An item can be fresh and still broken — a skill that delegates to another skill you never adopted stays "up to date" forever. `bin/check-integrity` is static and offline, so run it after every adoption. `--strict` fails on warnings too.

## Uninstall

```bash
./uninstall.sh
```

Removes only the symlinks that point into this repo. If `install.sh` previously made backups, the most recent `.backup-*` for each removed symlink is restored automatically.

## Troubleshooting

- **Broken symlink in `~/.claude/`** — the repo was moved or deleted. Move it back, or run `./uninstall.sh` (it's a no-op if the symlink targets are gone) and re-clone.
- **`settings.json` not loading** — check `readlink ~/.claude/settings.json` resolves into this repo, then validate JSON with `python3 -m json.tool < ~/.claude/settings.json`.
- **Statusline missing** — `chmod +x user/{mac,linux}/statusline-command.sh` and re-run `./install.sh`.
