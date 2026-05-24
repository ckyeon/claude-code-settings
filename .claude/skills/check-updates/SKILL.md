---
name: check-updates
description: Check upstream freshness of provenance-tracked items and investigate whether tracked paths actually changed. Use when the user asks to check for updates, detect outdated provenance pins, or wants to know if upstream repos have new changes relevant to adopted items. Also trigger when the user mentions "outdated", "stale", "upstream changes", "new version", or asks about the status of adopted skills, plugins, or MCP servers.
---

# check-updates

Check whether provenance-pinned upstream commits are behind HEAD, then investigate whether the tracked paths actually changed.

## Workflow

### Step 1 — Fast SHA check

Run the script from the repo root:

```
bin/check-updates
```

This compares pinned commits against upstream HEAD via `git ls-remote` (no clone). It outputs items grouped by source repo, marking each as up-to-date or outdated. Exit code 1 means some items are outdated.

If everything is up to date, report that and stop.

### Step 2 — Deep investigation (outdated items only)

For each unique outdated source repo, clone blobless into a temp dir:

```bash
TMPDIR=$(mktemp -d)
git clone --filter=blob:none --no-checkout <source_url> "$TMPDIR"
```

Then for each outdated item from that repo, check whether the tracked path actually changed:

```bash
git -C "$TMPDIR" log --oneline <pinned_sha>..<head_sha> -- <path_in_source>
```

If the log is empty, the tracked path had no changes — the pin is behind but the content is identical. If the log has commits, those are real changes to the tracked content.

Clean up each temp dir when done: `rm -rf "$TMPDIR"`

### Step 3 — Present results

Group findings into two categories:

**업데이트 필요** — items where the tracked path has actual commits:
- Show the commit list from `git log`
- For `copied` items: emphasize that local files may be stale since they were copied from upstream
- For `inspired-by` items: note that upstream content changed; the provenance pin should be updated

**pin만 뒤처짐 (실질 변경 없음)** — items where the path had no changes:
- These can be updated to the latest pin for accuracy, but there's no urgency

When many items share the same source and pin (e.g., 27 phaser skills), summarize them as a group rather than listing each individually.

### Step 4 — Offer next steps

For items with real changes, suggest the `bin/adopt` command to update:

```bash
bin/adopt \
  --from <source_url> \
  --commit <new_head_sha> \
  --path <path_in_source> \
  --to <local_path> \
  --mode <copied|inspired-by> \
  --license <SPDX>
```

For `copied` items, this also pulls the new file contents. For `inspired-by` items, it updates only the provenance pin.

Wait for the user to decide which items to update — do not run `bin/adopt` automatically.
