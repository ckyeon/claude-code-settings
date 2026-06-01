# Track the OpenAI codex plugin from a third-party marketplace

Adopt `codex@openai-codex` (OpenAI's Codex-in-Claude-Code plugin) into the user
scope using the provenance-only pattern, pinned to upstream commit `807e03ac`
(v1.0.4). This is the first tracked plugin from a non-Anthropic marketplace.

## Considered options

- **Provenance-only sidecar (chosen)** — matches how the existing four marketplace
  plugins are tracked: a `README.md` + `.provenance.json` under
  `user/shared/plugins/codex/`, no source vendored. `/plugin install` handles
  activation; `bin/sources-index` and the `install.sh`/`uninstall.sh` hints pick it
  up automatically.
- **Split adoption (copy commands/agent out)** — rejected. The plugin ships a
  Node/TypeScript companion runtime plus hooks that can't be split sensibly, the
  same reason [[hookify]] is tracked whole rather than by artifact.

## Consequences

- Activation differs from the `claude-plugins-official` plugins: it requires
  `/plugin marketplace add openai/codex-plugin-cc` before `/plugin install`. That
  marketplace registration is captured in `user/shared/settings.json` under
  `extraKnownMarketplaces` (tracked), and the enable flag under `enabledPlugins`.
- Adds a runtime dependency on Node.js 18.18+ and a ChatGPT subscription / OpenAI
  API key — but only when the plugin's commands are invoked. Auth stays
  machine-local and is never committed.
- Future `bin/check-updates` runs will compare against `openai/codex-plugin-cc`
  HEAD, surfacing version bumps past v1.0.4.

## References

- [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc)
- [[0003-adr-for-every-change]]
