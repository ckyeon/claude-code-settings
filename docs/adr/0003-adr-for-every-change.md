# Record an ADR for every change, not selectively

The root CLAUDE.md "Record a decision" workflow now mandates an ADR for **every** change to this repo, replacing the selective criteria (rationale-not-obvious **and** one of three conditions) introduced in commit `afb22cf`. The user wants a complete history of their decision records, not a minimal log.

## Considered options

- Keep the selective criteria (`afb22cf`) — rejected: it leaves many changes undocumented (e.g., this session's `user/shared/CLAUDE.md` edit initially shipped without an ADR and had to be backfilled as [[0002-re-expand-user-claude-md]]), defeating the goal of a full decision history.
- Mandate an ADR for every change — chosen.

## Consequences

- More ADRs, including for small changes; the `docs/adr/` log becomes the canonical decision history.
- To keep this cheap, ADR depth scales with the decision: trivial changes get a one-line ADR, consequential ones use the optional Considered Options / Consequences sections.
- This is a deliberate, scoped exception to ADR 0001's "minimize context noise" ethos — that principle governs what loads into agent context (CLAUDE.md, skills); ADR files in `docs/adr/` do not load into context, so a fuller log costs nothing at runtime.

## References

- [[0001-trim-user-claude-md]]
- [[0002-re-expand-user-claude-md]]
