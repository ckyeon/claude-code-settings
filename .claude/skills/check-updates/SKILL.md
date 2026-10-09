---
name: check-updates
description: Check upstream freshness of provenance-tracked items, investigate whether tracked paths actually changed, and surface structural changes in the source repos (skills and plugins added or removed upstream). Use when the user asks to check for updates, detect outdated provenance pins, or wants to know if upstream repos have new changes relevant to adopted items. Also trigger when the user mentions "outdated", "stale", "upstream changes", "new version", new or removed upstream skills, or asks about the status of adopted skills, plugins, or MCP servers.
---

# check-updates

Check whether provenance-pinned upstream commits are behind their comparison target (upstream HEAD, or the release or marketplace sha a sidecar's `track` names), then investigate whether the tracked paths actually changed, how much the changes matter, and how the source repos themselves evolved around them (skills and plugins added or removed upstream).

The deterministic work (clones, logs, diffs) lives in `bin/check-updates`; this skill adds the judgment layer on top via subagents, keeping raw git output out of the main session's context.

## Workflow

### Step 1 — Fast SHA check

Run the script from the repo root:

```
bin/check-updates
```

This compares pinned commits against upstream HEAD via `git ls-remote`, without cloning except a shallow marketplace clone for items tracked by marketplace. Exit code 1 means some items are outdated.

Items whose sidecar sets a top-level `track` are compared against a different target, labeled on their line: `[release vX.Y.Z]` for the newest stable tag, `[<marketplace> pin]` for the sha their marketplace pins (see `docs/PROVENANCE.md`). A `?` line means the target could not be found, and the line gives the reason. Report it as unresolved, not as up to date.

If everything is up to date, report that and stop.

### Step 2 — Deep scan (outdated items only)

```
bin/check-updates --deep
```

This re-runs the fast check, then clones each outdated source blobless into a temp workdir, and for every outdated item compares the tracked path's tree (or blob) SHA at pin and head to classify it:

- **changed** — the tracked path's content differs. The workdir gets `items/<dest>/log.txt` (`git log <pin>..<head> -- <path>`), plus `items/<dest>/upstream.diff` (`git diff <pin> <head> -- <path>`) for `copied` items. When the pin sits on a side branch and only the pin's side changed the path, `log.txt` is a `--left-right <pin>...<head>` log instead, where `<` marks pin-side commits.
- **pin-only** — the pin is behind but the tracked path's content is identical. This holds even when `git log <pin>..<head>` lists commits, as with a release tag cut on a side branch whose edit reached main as a different commit.

It also scans **upstream structure** for each outdated source, in two passes. Both compare pin vs head, so entries that predate the pin and were deliberately left unadopted never show up as noise.

- **Next to tracked paths** — the parent directories of tracked paths are listed, and the report shows entries the upstream **added** (`NEW`) or **removed** (`REMOVED`, with `** adopted here **` when the removed entry is one this repo adopted).
- **Anywhere else in the repo** — every directory that gained a `SKILL.md` or `.claude-plugin/plugin.json` shows as `NEW … (outside tracked dirs)`, such as a skill in a category directory this repo adopted nothing from. An entry nested inside another skill or plugin is reported as that outer entry.

Agents, commands, hooks, and MCP servers carry neither marker file, so the scan sees them only inside the tracked paths' parent directories. Whole-repo items (`path: "."`) are skipped because their git log already covers everything.

The workdir path is printed at the end and contains `deep.json` (machine-readable records: per-item facts under `items`, structural scan results under `structure`, where each record's `scope` is `sibling` for the first pass and `elsewhere` for the second) plus the clones themselves. Do not re-derive any of this by hand in the main session — read `deep.json` for the facts.

### Step 3 — Judgment fan-out (changed items + structural changes)

Pin-only items need no judgment. Spawn one subagent per source repo that has **changed** items or **structural** entries (`NEW`/`REMOVED`) — all in a single message so they run in parallel. Each agent gets:

- the repo label and its clone dir under `<workdir>/clones/`
- the list of its changed items: local dest, `item_dir` (log.txt / upstream.diff), mode, pinned and head SHAs
- its `structure` records from `deep.json`: added/removed entries, scope, pin, head

Instruct each agent to:

1. Read `log.txt` and `upstream.diff` for each item; run extra `git` commands in the clone if the diff alone is ambiguous. For `copied` items it may also compare against the local dest to spot local drift.
2. Classify each item's change: **substantive** (behavior/content meaningfully different) vs **cosmetic** (formatting, phrasing, em-dashes).
3. For each `NEW` entry: read it at head in the clone (e.g. `git show <head>:<path>/SKILL.md`) and return a 1-line description plus an adoption-worthiness call, given what's already adopted from that repo. For an `elsewhere` entry, also say what its directory is for, read from a README there or the repo's top-level README. A beta bucket or the repo's own contributor tooling weighs against adoption.
4. For each `REMOVED` entry: find out what happened (`git log --oneline <pin>..<head> --diff-filter=DR -- <path>` — deleted outright, renamed/moved, or folded into another item). Entries marked `** adopted here **` are the priority: the local copy has lost its upstream.
5. Flag risks — especially changes to how skills reference other skills (`/name` phrasing), which interact with `bin/check-integrity`'s cross-reference scan, and any new dependency an updated item delegates to (the "adopt what it delegates to" rule).
6. Return ONLY a compact summary: per item/entry, a verdict, a 1-2 line rationale, and any risk flags. Never dump diffs or full logs back.

### Step 4 — Present results

Group findings into three categories:

**업데이트 필요** — changed items, enriched with the agents' verdicts (substantive vs cosmetic, risk flags). For `copied` items emphasize that local files are stale; for `inspired-by` items only the provenance pin needs updating.

**upstream 구조 변경** — `NEW`/`REMOVED` entries, with the agents' one-line descriptions and verdicts. Lead with any `** adopted here **` removal — the local copy has lost its upstream and the user must decide what to do with it. Each `NEW` entry is its own adopt-or-skip decision: give it a line with the description and your recommendation, and ask the user about it directly, including when it matters only because an updated item routes to it. End the category with one line stating the scan's coverage, using the limits Step 2 describes.

**pin만 뒤처짐 (실질 변경 없음)** — pin-only items. These can be re-pinned for accuracy, but there's no urgency.

When many items share the same source and pin (e.g., 28 phaser skills), summarize them as a group rather than listing each individually.

### Step 5 — Offer next steps

For items worth updating, suggest `bin/re-pin` with their local paths:

```bash
bin/re-pin <local_path> [<local_path>...]
```

Each item moves to its comparison target, the `head` value `deep.json` reports for it, so no SHA needs copying. For `copied` items this also pulls the new file contents. For `inspired-by` items it updates only the pin. `bin/re-pin` refuses a `copied` item whose local copy differs from upstream at the old pin and lists the difference. Report that to the user rather than passing `--overwrite-local` yourself.

For `NEW` entries worth adopting, use `bin/adopt --from <source_url> --commit <sha> --path <upstream_path> --to <local_path> --mode copied --license <SPDX>`. For `REMOVED` entries that are adopted here, lay out the options: keep the local copy as an orphaned fork (the sidecar stays as history), delete it, or re-adopt from the renamed/moved path the agent found.

Wait for the user to decide which items to update. Run neither `bin/re-pin` nor `bin/adopt` before that. Once decisions are made (or the session moves on), clean up the workdir: `rm -rf <workdir>`.
