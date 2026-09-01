---
name: check-updates
description: Check upstream freshness of provenance-tracked items and investigate whether tracked paths actually changed. Use when the user asks to check for updates, detect outdated provenance pins, or wants to know if upstream repos have new changes relevant to adopted items. Also trigger when the user mentions "outdated", "stale", "upstream changes", "new version", or asks about the status of adopted skills, plugins, or MCP servers.
---

# check-updates

Check whether provenance-pinned upstream commits are behind HEAD, then investigate whether the tracked paths actually changed and how much the changes matter.

The deterministic work (clones, logs, diffs) lives in `bin/check-updates`; this skill adds the judgment layer on top via subagents, keeping raw git output out of the main session's context.

## Workflow

### Step 1 — Fast SHA check

Run the script from the repo root:

```
bin/check-updates
```

This compares pinned commits against upstream HEAD via `git ls-remote` (no clone). Exit code 1 means some items are outdated.

If everything is up to date, report that and stop.

### Step 2 — Deep scan (outdated items only)

```
bin/check-updates --deep
```

This re-runs the fast check, then clones each outdated source blobless into a temp workdir, and for every outdated item runs `git log <pin>..<head> -- <path>` to classify it:

- **changed** — the tracked path has real commits. The workdir gets `items/<dest>/log.txt`, plus `items/<dest>/upstream.diff` (`git diff <pin> <head> -- <path>`) for `copied` items.
- **pin-only** — the pin is behind but the tracked path is untouched.

The workdir path is printed at the end and contains `deep.json` (machine-readable records: local path, source, pin, head, mode, license, commit count, status, item dir) plus the clones themselves. Do not re-derive any of this by hand in the main session — read `deep.json` for the facts.

### Step 3 — Judgment fan-out (changed items only)

Pin-only items need no judgment. For **changed** items, spawn one subagent per source repo that has them — all in a single message so they run in parallel. Each agent gets:

- the repo label and its clone dir under `<workdir>/clones/`
- the list of its changed items: local dest, `item_dir` (log.txt / upstream.diff), mode, pinned and head SHAs

Instruct each agent to:

1. Read `log.txt` and `upstream.diff` for each item; run extra `git` commands in the clone if the diff alone is ambiguous. For `copied` items it may also compare against the local dest to spot local drift.
2. Classify each item's change: **substantive** (behavior/content meaningfully different) vs **cosmetic** (formatting, phrasing, em-dashes).
3. Flag risks — especially changes to how skills reference other skills (`/name` phrasing), which interact with `bin/check-integrity`'s cross-reference scan, and any new dependency an updated item delegates to (the "adopt what it delegates to" rule).
4. Return ONLY a compact summary: per item, a verdict, a 1-2 line rationale, and any risk flags. Never dump diffs or full logs back.

### Step 4 — Present results

Group findings into two categories:

**업데이트 필요** — changed items, enriched with the agents' verdicts (substantive vs cosmetic, risk flags). For `copied` items emphasize that local files are stale; for `inspired-by` items only the provenance pin needs updating.

**pin만 뒤처짐 (실질 변경 없음)** — pin-only items. These can be re-pinned for accuracy, but there's no urgency.

When many items share the same source and pin (e.g., 28 phaser skills), summarize them as a group rather than listing each individually.

### Step 5 — Offer next steps

For items worth updating, suggest the `bin/adopt` command:

```bash
bin/adopt \
  --from <source_url> \
  --commit <new_head_sha> \
  --path <path_in_source> \
  --to <local_path> \
  --mode <copied|inspired-by> \
  --license <SPDX>
```

For `copied` items this also pulls the new file contents; for `inspired-by` items it updates only the provenance pin.

Wait for the user to decide which items to update — do not run `bin/adopt` automatically. Once decisions are made (or the session moves on), clean up the workdir: `rm -rf <workdir>`.
