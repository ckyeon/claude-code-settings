# Derive plugin install hints from settings.json instead of printing placeholders

`install.sh` / `uninstall.sh` now emit the exact `/plugin marketplace add` and
`/plugin install` commands per tracked plugin, resolving each plugin's marketplace
from `enabledPlugins` and each third-party marketplace's repo from
`extraKnownMarketplaces`. Previously they listed bare plugin names under a
`/plugin install <name>@<marketplace>` placeholder, which silently omitted the
`marketplace add` step that third-party plugins require.

## Context

Setting up a fresh machine, `/plugin install codex@openai-codex` failed with
`Marketplace "openai-codex" not found`. The placeholder output gave no way to know
which of the seven tracked plugins needed a marketplace registered first, nor what
to register it as — the marketplace *name* (`openai-codex`) is not the argument
`/plugin marketplace add` takes (`openai/codex-plugin-cc`). `extraKnownMarketplaces`
in `user/shared/settings.json` is tracked (see [[0004-track-codex-plugin]]) but is
not a substitute for registering the marketplace on the machine.

## Considered options

- **Derive from the tracked settings.json files (chosen)** — the mapping already
  exists there and is authoritative, so hints can't drift from what's enabled. User
  scope comes from `user/shared/settings.json`; project-scope plugins like
  `typescript-lsp` resolve from `project-templates/*/.claude/settings.json`, and are
  labelled as such rather than presented as user-scope installs.
- **Add a `marketplace` field to the sidecar** — rejected. It would duplicate
  settings.json and invite the two to disagree, and the marketplace is activation
  data, not provenance.
- **Derive the marketplace from the sidecar's source URL** — rejected as unsound:
  `openai/codex-plugin-cc` is registered as `openai-codex`, so repo name and
  marketplace name don't correspond.

## Consequences

- A tracked plugin absent from every `enabledPlugins` prints as a warning naming its
  README rather than being silently skipped, so the two sources stay visibly in sync.
- `list_tracked_plugins` returns `name|marketplace|source|scope` rows instead of bare
  names. The separator is `|`, not a tab: tab is an IFS whitespace character, so
  `read` coalesces runs of it and a built-in marketplace's empty `source` field would
  shift `scope` into its place — which is exactly the bug the first cut shipped.
- Adding a plugin to `user/shared/plugins/` without the matching `settings.json`
  entries now yields incomplete hints; the tracking workflow in `CLAUDE.md` says so.
- Verified by running both scripts against a throwaway `HOME`, covering built-in,
  third-party, project-scope, and unknown-marketplace rows.

## References

- [[0004-track-codex-plugin]], [[0005-track-understand-anything-plugin]]
- [[0003-adr-for-every-change]]
