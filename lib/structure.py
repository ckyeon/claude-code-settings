"""Upstream structure comparison shared by bin/check-updates and bin/adopt.

Finds the skills and plugins an upstream added between two commits outside
the directories the sibling pass already compares.
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
