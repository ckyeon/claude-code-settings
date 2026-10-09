"""What changed in an upstream's structure between two commits.

bin/check-updates and bin/adopt both ask this before a pin moves: which
entries appeared or vanished next to the paths this repo tracks, and which
skills or plugins appeared anywhere else. changes() is the whole answer.
"""
import os

# A directory holding one of these is a skill or a plugin.
MARKERS = ("/SKILL.md", "/.claude-plugin/plugin.json")


def marker_dirs(run_git, sha):
    """Every directory holding a marker file at sha, or None if git fails.

    run_git(*args) runs git in the upstream clone and returns the completed
    process. Only trees are read, so a blobless clone fetches nothing.
    """
    res = run_git("ls-tree", "-r", "-z", "--name-only", sha)
    if res.returncode != 0:
        return None
    return {p[:-len(m)] for p in res.stdout.split("\0") for m in MARKERS if p.endswith(m)}


def under(p, base):
    return p == base or p.startswith(base + "/")


def ancestors(p):
    while "/" in p:
        p = p.rsplit("/", 1)[0]
        yield p


def added_elsewhere(old_markers, new_markers, tracked, reported):
    """Marker directories added between two commits that nothing else reports.

    tracked is every upstream path this repo tracks from the source, at any
    pin. reported is what the sibling pass already lists as new. Left out:

    - an entry under a reported one, or under a tracked path, whose own diff
      covers it;
    - a direct child of a tracked path's parent directory. It is a sibling,
      and the sibling pass reports it against the pin of the items living
      there, which may differ from the pin being compared here;
    - an entry nested inside another skill or plugin.
    """
    tracked_parents = {os.path.dirname(t) for t in tracked}
    known = set(reported) | set(tracked)
    return sorted(
        d for d in new_markers - old_markers
        if not any(under(d, k) for k in known)
        and os.path.dirname(d) not in tracked_parents
        and not any(a in new_markers for a in ancestors(d)))


def _entries(run_git, sha, root):
    """Names directly under root at sha, as full paths. None if git fails."""
    args = ["ls-tree", "-z", "--name-only", sha]
    if root:
        args += ["--", root.rstrip("/") + "/"]
    res = run_git(*args)
    if res.returncode != 0:
        return None
    return {p for p in res.stdout.split("\0") if p}


def changes(run_git, old, new, moving, tracked):
    """Structure changes between commits old and new, as a list of records.

    moving is the tracked paths whose pin is moving from old to new. tracked
    is every path this repo tracks from the source, at any pin.

    Two passes, both comparing old against new so entries that predate old
    never appear:

    - "sibling": one record per parent directory of a moving path, listing the
      entries added and removed directly under it. removed_tracked names the
      removed entries this repo tracks, which have lost their upstream.
    - "elsewhere": one record for the skills and plugins added outside those
      directories (see added_elsewhere).

    Each record is {"root", "scope", "added", "removed", "removed_tracked"}.
    A whole-repo path (".") has no siblings and is ignored. A directory or
    commit git cannot list is skipped rather than reported as empty.
    """
    tracked = set(tracked)
    records, reported = [], set()
    roots = sorted({os.path.dirname(p) for p in moving if p and p != "."})
    for root in roots:
        before, after = _entries(run_git, old, root), _entries(run_git, new, root)
        if before is None or after is None:
            continue
        added, removed = sorted(after - before), sorted(before - after)
        if not added and not removed:
            continue
        reported.update(added)
        records.append({
            "root": root or ".",
            "scope": "sibling",
            "added": added,
            "removed": removed,
            "removed_tracked": sorted(p for p in removed if p in tracked),
        })
    if roots:
        old_markers, new_markers = marker_dirs(run_git, old), marker_dirs(run_git, new)
        if old_markers is not None and new_markers is not None:
            elsewhere = added_elsewhere(old_markers, new_markers, tracked, reported)
            if elsewhere:
                records.append({"root": ".", "scope": "elsewhere", "added": elsewhere,
                                "removed": [], "removed_tracked": []})
    return records
