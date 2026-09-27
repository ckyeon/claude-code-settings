# remotion (provenance-only)

This directory exists for provenance tracking only. The remotion plugin is **not** vendored here.

## What it does

Remotion's official Claude Code plugin: the Remotion Agent Skills for building programmatic videos with React. It ships 12 skills; `remotion-best-practices` routes to the rest (`remotion-create`, `remotion-render`, `remotion-captions`, `remotion-markup`, `remotion-maps`, and others). The same skills are published as `remotion-dev/skills` for `npx skills add`; at plugin version 4.0.529 the two differ only in a few map example `.tsx` assets the plugin leaves out.

In the video template it is the React alternative to HyperFrames for animation overlays. See `project-templates/video/.claude/skills/edit-by-transcript/references/look.md`.

## License

The plugin manifests (`plugin.json`, `marketplace.json`) declare `"license": "MIT"`; the repo itself has no LICENSE file. That covers the skills. Rendering videos uses the `remotion` npm packages, which are under the Remotion License (`remotion-dev/remotion/LICENSE.md`): free for individuals, for-profit organizations with up to 3 employees, and non-profits; other companies need a company license.

## How it's actually installed

Project scope only, from inside a project created from `project-templates/video/`. Its marketplace is third-party, so it has to be added once per machine first:

```
claude plugin marketplace add remotion-dev/claude-code-plugin
claude plugin install remotion@remotion --scope project
```

Remotion's docs (remotion.dev/docs/ai/claude-code-plugin) give these two commands without `--scope`, which installs at user scope and turns the plugin on in every project. The template's `.claude/settings.json` lists the marketplace under `extraKnownMarketplaces`, which lets `install.sh` print the `marketplace add` line, but does not register it on the machine.

## Where it's enabled

Project-scope only (not user-scope). Enabled in:
- `project-templates/video/.claude/settings.json`

## Pinning

Third-party marketplaces do not auto-update by default, so installed copies stay at the version installed until someone runs `claude plugin update remotion@remotion`. Re-pin this record to the new HEAD of `remotion-dev/claude-code-plugin`; the plugin root is the repo root.

## Why a sidecar but no source

Vendoring the skills would add about 2.3 MB and 280 files, most of them copies that `remotion-best-practices` embeds from `remotion-markup` and `remotion-maps`. The plugin keeps them out of this repo. See [[../hyperframes]] for the same choice.
