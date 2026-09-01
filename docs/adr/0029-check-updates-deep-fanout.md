# 0029 — Split check-updates deep investigation into `--deep` + per-repo judgment subagents

The `/check-updates` skill's Step 2 (clone outdated sources, check whether tracked paths changed) was prose instructions executed inline by the main session — ad-hoc, token-heavy, and it flooded the conversation with provenance dumps and git logs. The deterministic part is now `bin/check-updates --deep`: parallel blobless clones, per-item `git log <pin>..<head> -- <path>` classification (changed / pin-only), `upstream.diff` for changed `copied` items, and a `deep.json` summary, all left in a printed temp workdir. The skill keeps only the judgment layer: one subagent per source repo with changed items reads the prepared logs/diffs (and the shared clone) and returns compact verdicts — substantive vs cosmetic, risk flags — so the main context stays clean and clones are never duplicated per agent.

## Consequences

- `--deep` shares one clone across duplicate source-URL spellings (`.git` suffix) by keying clone dirs on the sanitized `owner/repo` label.
- Upstream content diffs are generated only for `copied` items with a non-`.` path; for `inspired-by` items the commit log is the signal and a whole-repo diff would be noise.
- Pin-only items bypass the judgment fan-out entirely.
- The workdir is deliberately not auto-deleted — agents and the user inspect it; the skill's last step cleans it up.
