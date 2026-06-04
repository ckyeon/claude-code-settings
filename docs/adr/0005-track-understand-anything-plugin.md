# Track the understand-anything plugin from a third-party marketplace

Adopt `understand-anything@understand-anything` (Lum1104's codebase-to-knowledge-graph
plugin) into the user scope using the provenance-only pattern, pinned to upstream
commit `7a3b7511` (v2.7.6). This is the second tracked plugin from a non-Anthropic
marketplace, after [[0004-track-codex-plugin]].

## Considered options

- **Provenance-only sidecar (chosen)** — matches how the existing marketplace plugins
  are tracked: a `README.md` + `.provenance.json` under
  `user/shared/plugins/understand-anything/`, no source vendored. `/plugin install`
  handles activation; `bin/sources-index` and the `install.sh`/`uninstall.sh` hints
  pick it up automatically.
- **Copy a standalone skill out of `understand-anything-plugin/skills/`** — rejected.
  The plugin's skills are coupled to its bundled commands (`/understand`,
  `/understand-dashboard`), agents, hooks, and a TypeScript pnpm-workspace runtime; a
  lone `SKILL.md` would be dangling and non-functional. Same reason [[hookify]] and
  [[0004-track-codex-plugin]] are tracked whole rather than by artifact.

## Consequences

- Activation requires `/plugin marketplace add Lum1104/Understand-Anything` before
  `/plugin install understand-anything`. The marketplace registration is captured in
  `user/shared/settings.json` under `extraKnownMarketplaces` (tracked), and the enable
  flag under `enabledPlugins`.
- No API key is required — the plugin analyzes local code in-session. It bundles a
  Node/TypeScript runtime, so Node is needed wherever that runtime executes.
- Future `bin/check-updates` runs compare against `Lum1104/Understand-Anything` HEAD
  (path `understand-anything-plugin`), surfacing version bumps past v2.7.6.

## References

- [Lum1104/Understand-Anything](https://github.com/Lum1104/Understand-Anything)
- [[0004-track-codex-plugin]]
- [[0003-adr-for-every-change]]
