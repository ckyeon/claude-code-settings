# hyperframes (provenance-only)

This directory exists for provenance tracking only. The hyperframes plugin is **not** vendored here.

## What it does

HeyGen's HyperFrames: write HTML compositions (GSAP and other animation runtimes), render them to video. The renderer seeks each frame in headless Chrome and encodes with FFmpeg. The plugin ships 21 skills, among them `hyperframes`, `hyperframes-cli`, `embedded-captions`, `motion-graphics` and `talking-head-recut`.

In the video template it produces animation overlays: `edit-by-transcript` renders each one into `edit/animations/slot_<id>/` and lists the file under the EDL's `overlays`.

## Prerequisites

The upstream README states "**Requirements:** Node.js 22+, FFmpeg". The video template's `check_env.sh` covers FFmpeg but not Node.

## How it's actually installed

Project scope only, from inside a project created from `project-templates/video/`:

```
claude plugin install hyperframes@claude-plugins-official --scope project
```

Or, in a session, `/plugin install hyperframes@claude-plugins-official` and choose **Install for all collaborators on this repository (project scope)**. The shell command defaults to user scope and the session panel offers user scope first; either would turn the plugin on in every project. The template's `.claude/settings.json` enables the plugin but does not download it, so each machine runs the install once (Claude Code docs, "Install and manage plugins" > "Choose an install scope").

## Where it's enabled

Project-scope only (not user-scope). Enabled in:
- `project-templates/video/.claude/settings.json`

## Pinning

The `claude-plugins-official` marketplace lists hyperframes as a `url` source, `https://github.com/heygen-com/hyperframes.git`, pinned to a `sha`. The `.provenance.json` next to this README pins that same sha. `claude-plugins-official` auto-updates by default, so installed copies follow the marketplace's sha, not this record. When re-pinning, read the new sha from the marketplace's `.claude-plugin/marketplace.json`, not from the upstream repo's HEAD.

## Why a sidecar but no source

21 skills plus a CLI that the plugin keeps current. Copying them here would pin a snapshot the marketplace already manages. See [[../hookify]] for the same reasoning.
