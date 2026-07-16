# Enable fullscreen TUI in user-scope settings

Add `"tui": "fullscreen"` to `user/shared/settings.json` so every machine renders
Claude Code to a separate full-screen buffer (flat memory over long sessions, mouse
scroll/selection, no scrollback flicker) instead of the default classic line-based
mode.

## Context

The setting was present in this machine's pre-existing `~/.claude/settings.json` but
absent from the repo, so `install.sh` backed the file up and replaced it, dropping
the setting. Rather than restore it per-machine, we track it in the shared settings —
the behaviour is wanted everywhere, not just here.

## Consequences

- Applies on both mac and linux via the single shared `settings.json`. If a future
  machine's terminal renders fullscreen poorly, override with `"tui"` in that
  machine's `settings.local.json` (untracked).
- Ignored automatically when screen-reader mode (`axScreenReader`) is on, so it does
  not compromise accessibility.

## References

- [[0003-adr-for-every-change]]
