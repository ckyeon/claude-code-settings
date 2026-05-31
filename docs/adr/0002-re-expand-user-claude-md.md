# Re-expand user/shared/CLAUDE.md with net-new agent rules (extends ADR 0001)

Added a `**Tone:**` callout, question-tiering to §1.1, and a new "Before and After Acting" section. 31 → 39 lines. This does not reverse ADR 0001: every added rule differs from Claude Code's defaults, which is exactly what ADR 0001 says a user-scope CLAUDE.md is for.

## Considered options

- Append the original ~50-line "Personal Agent Instructions" block as-is — rejected: ~40-50% restated the existing file or system-prompt defaults, re-introducing the "over-specified CLAUDE.md" failure ADR 0001 fought.
- Don't add anything — rejected: the kernel (no-praise tone, question tiering, ask-first list, premortem, gated post-change report) is genuinely net-new preference absent from both defaults and the existing file.
- Polish the kernel into the existing structure — chosen.

## Specific keep/drop calls

- Dropped the External Content / prompt-injection guard: the harness already treats external content as data, so it failed the "would removing this cause a mistake?" test from ADR 0001.
- Relaxed §1.1's hard "1-3 questions" cap to fit the blocker/refinement tiering.
- Gated the post-change report to non-trivial work to preserve the existing "skip ceremony" calibration.

## References

- [[0001-trim-user-claude-md]]
