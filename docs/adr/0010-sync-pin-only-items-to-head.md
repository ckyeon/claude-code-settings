# Sync pin-only items to HEAD, reversing ADR 0006

Bump the 39 provenance items whose tracked path has no upstream commits since the
pinned SHA — the vendored content already matches, only the pin is stale. This
reverses [[0006-sync-outdated-provenance-2026-06-09]], which deliberately left the
same class of item untouched and recorded that they would keep reporting outdated.

## Context

ADR 0006 skipped pin-only items on the reasoning that a pin bump with no content
change is churn. The cost of that choice compounds: on the `2026-07-16` run, 39 of
the 17 outdated groups' items were pin-only noise that had to be re-investigated —
cloning each source and running `git log <pin>..HEAD -- <path>` — purely to
re-derive "nothing changed", a fact the previous run already established. The signal
worth acting on (five retired paths, seven genuinely-changed items) was buried in it.

A pin is not only a record of where content came from; it is the baseline
`check-updates` diffs against. Leaving it behind makes every future run re-do work.

## Considered options

- **Sync all 39 (chosen)** — future `check-updates` output reports only real drift.
  The cost is one-time: ~39 `bin/adopt` runs, each re-cloning its source.
- **Hold ADR 0006** — rejected. It optimises for a small sidecar diff today at the
  price of re-investigating the same items on every run, forever.
- **Sync only the five `claude-plugins-official` plugins** — rejected as a half
  measure: the 28 phaser skills are the bulk of the noise, so skipping them leaves
  the problem in place.

## Consequences

- Each of the 39 sidecars gains a `2026-07-16` entry recording that the content was
  verified identical at the new HEAD. Prior entries stay as history, so the sidecars
  grow by one entry per sync — the churn ADR 0006 was avoiding, accepted here as the
  price of a trustworthy baseline.
- The next `check-updates` should be near-silent. A future outdated report then means
  something actually moved, which is the point.
- `bin/adopt` re-clones per invocation, so a bulk sync is dominated by clone time
  (phaser × 28). If this becomes routine, `bin/adopt` wants a batch mode that clones
  each source once — not built now, since a sync this large should be rare once the
  baseline is current.
- Sources were read back from each sidecar rather than retyped, so the recorded URL
  form (`…claude-plugins-official` vs `….git`) is preserved and `check-updates`
  keeps grouping them as before.

## References

- [[0006-sync-outdated-provenance-2026-06-09]] — superseded on this point
- [[0009-follow-upstream-renames-and-retirements]] — the same run's real drift
- [[0003-adr-for-every-change]]
