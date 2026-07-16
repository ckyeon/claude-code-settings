# Prune the destination on `copied` re-adoption

`bin/adopt --mode copied` now empties the destination folder (keeping
`.provenance.json`) before copying upstream content in. Previously it ran only
`cp -R "$SRC/." "$TO/"`, which overwrites but never deletes, so every file upstream
removed since the pinned commit stayed local forever.

## Context

Re-adopting the mattpocock skills at `e9fcdf95` left eight orphaned files behind —
`tdd/refactoring.md` (upstream dropped the refactor stage from red-green-refactor),
`tdd/deep-modules.md`, `tdd/interface-design.md`, `grill-with-docs/ADR-FORMAT.md`,
`grill-with-docs/CONTEXT-FORMAT.md`, and three under
`improve-codebase-architecture/`. They referenced only each other, so nothing
surfaced them as broken; they simply sat in `~/.claude/skills/` as content the
upstream author had deleted. The [[0006-sync-outdated-provenance-2026-06-09]] sync
shipped the same class of leftover (`CONTEXT-FORMAT.md` dates from it).

This matters more for skills than for ordinary vendored code: every file under a
skill directory is a candidate for loading into Claude's context, so a stale
reference file is stale instructions.

## Considered options

- **Prune before copy, gated on an existing sidecar (chosen)** — `find "$TO"
  -mindepth 1 -maxdepth 1 ! -name '.provenance.json' -exec rm -rf {} +`. The gate
  means a mistyped `--to` can only ever clear a directory this repo already tracks;
  a first-time adoption into a new or unrelated path never triggers a delete.
- **`rsync -a --delete`** — rejected: introduces a dependency outside the Python 3
  stdlib + bash budget, and rsync is not guaranteed present on a bare macOS box.
- **Leave it and prune by hand** — rejected. It already failed silently twice; the
  leftovers are invisible unless someone diffs against upstream, which is exactly
  what a tool should do.

## Consequences

- `copied` destinations are now true mirrors of the upstream path at the pinned
  commit. Local edits to a `copied` item are erased on the next re-adoption — that
  was already the intent of `copied` (fork it or use `inspired-by` instead), but the
  old behaviour hid it.
- Verified by planting a stale file and directory under `user/shared/skills/tdd`,
  re-adopting, and confirming both vanished while the sidecar survived.
- `file` destinations are unaffected — `cp` already replaces them wholesale.

## References

- [[0006-sync-outdated-provenance-2026-06-09]]
- [[0003-adr-for-every-change]]
