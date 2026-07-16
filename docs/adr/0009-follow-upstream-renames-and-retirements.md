# Follow upstream renames and retirements rather than fork

Five tracked skills no longer exist at their upstream path. Four mattpocock skills
are re-adopted under their new names (`diagnose` → `diagnosing-bugs`, `to-issues` →
`to-tickets`, `to-prd` → `to-spec`) or dropped (`zoom-out`, deleted upstream), and
the retired `next-best-practices` is replaced by the four skills Next.js now ships
in-repo.

## Context

The `2026-07-16` `check-updates` run reported 17 outdated pin groups. Investigating
each tracked path against upstream HEAD showed five paths that no longer resolve:

- mattpocock/skills reorganised its planning skills into `/to-spec` + `/to-tickets`
  (386d4ff), replaced `diagnose` with `diagnosing-bugs` (221ffca), and deleted
  `zoom-out` outright (e112a6b).
- vercel-labs/next-skills is now an empty shell whose README points at
  `vercel/next.js/tree/canary/skills` — the skills moved into the framework repo to
  stay version-matched instead of drifting separately.

`bin/adopt` against a path that no longer exists fails rather than doing something
silently wrong, so these needed a decision either way.

## Considered options

- **Follow upstream (chosen)** — re-adopt at the new paths, delete what upstream
  retired. Keeps `bin/check-updates` meaningful: every tracked item stays a live
  pointer at something real.
- **Keep the last-known copy as a fork** — rejected for these five. Nothing local
  depends on them, and a fork means owning content whose author has moved on.
  `zoom-out` in particular was deleted, not superseded.

## Consequences

- Skill invocations change: `/diagnose` → `/diagnosing-bugs`, `/to-issues` →
  `/to-tickets`, `/to-prd` → `/to-spec`. Muscle memory and any prose referencing the
  old names go stale; nothing in this repo referenced them outside their own
  directories and the generated `SOURCES.md`.
- `next-best-practices` (a single broad Next.js ruleset) is replaced by four
  narrower, task-specific skills — `next-cache-components-adoption`,
  `next-cache-components-optimizer`, `next-dev-loop`,
  `next-partial-prefetching-adoption`. This is a change in kind, not a rename: the
  old ruleset has no successor. The `nextjs` template's guidance surface shifts
  accordingly.
- The new Next.js source is `vercel/next.js` (MIT), replacing the `UNLICENSED`
  vercel-labs/next-skills pin — a licensing improvement, since the retired repo
  never carried one.
- Pinning skills to the framework's own repo means future `check-updates` runs track
  Next.js `canary`, which moves fast; expect these four to report outdated often.

## References

- [[0006-sync-outdated-provenance-2026-06-09]]
- [[0003-adr-for-every-change]]
