# Sync outdated provenance pins to upstream (2026-06-09 check-updates)

A `/check-updates` run on 2026-06-09 found 11 of 13 tracked sources behind upstream
HEAD. Deep investigation (`git log <pin>..<head> -- <path>`) showed only **8 items
had real commits to their tracked path**; the rest were pin-lag with byte-identical
content. We re-ran `bin/adopt` against those 8 to refresh the pins — and, for the four
`copied` items, the vendored files. The ~50 pin-only entries were left untouched.

## Synced items

| Dest | Source | Commit | Mode |
|---|---|---|---|
| `project-templates/nextjs/.claude/skills/core` | vercel-labs/agent-browser | `4ad28489 → 328ce8a9` | copied |
| `user/shared/skills/grill-with-docs` | mattpocock/skills | `b8be62ff → 2bf70051` | copied |
| `user/shared/skills/to-prd` | mattpocock/skills | `b8be62ff → 2bf70051` | copied |
| `project-templates/phaser/.claude/skills/v4-new-features` | phaserjs/phaser | `3d6ad031 → 9e67ded9` | copied |
| `user/shared/plugins/understand-anything` | Lum1104/Understand-Anything | `7a3b7511 → 5c1e35f9` | inspired-by |
| `user/shared/mcp/github` | github/github-mcp-server | `e091ea63 → 457f5993` | inspired-by |
| `user/shared/mcp/context7` | upstash/context7 | `7e956e59 → 428af3e0` | inspired-by |
| `user/shared/mcp/fetch` | modelcontextprotocol/servers | `b1e1eb1a → 275175cd` | inspired-by |

## Considered options

- **Update only the 8 changed-content items (chosen)** — the pin exists to track
  *content*, so bumping pins whose tracked path didn't change adds churn without
  meaning. `bin/check-updates`'s deep-investigation step exists precisely to draw
  this line.
- **Bump all 11 outdated pins for tidiness** — rejected. Would touch ~50 sidecars
  (anthropics plugins ×5, agent-skills ×6, phaser ×27, etc.) with no content delta,
  burying the four real content changes in noise.

## Consequences

- The four `copied` skills now carry upstream's latest content (e.g. phaser
  `v4-new-features` gains the `MULTIPLY_TWO` tint mode; agent-browser `core` gains
  vitals-output and command-reference updates).
- The four `inspired-by` pins move forward but vendor nothing — activation stays via
  `/plugin install` / `claude mcp add`. The bumps only re-baseline future
  `check-updates` diffs; the recorded registration commands are unaffected.
- Each sidecar's `provenance[]` gained a new `2026-06-09` entry; prior entries are
  retained as history.
- The deliberately-skipped pin-only items will keep reporting "outdated" on the next
  `check-updates` run — that is expected, not a regression.

## References

- [[0003-adr-for-every-change]]
- [[0005-track-understand-anything-plugin]]
