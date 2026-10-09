"""Is each item's pin behind its comparison target, and what moved upstream?

check() is the fast answer: one record per current pin, with its target and
whether the pin is behind it. investigate() is the deep answer for the pins
that are behind: did the tracked path's content change, and how did the
upstream's structure change around it.

Both return plain records. bin/check-updates renders them as text and writes
the deep ones to deep.json, which the check-updates skill reads. The record
fields are therefore an interface: change them here and in that skill together.
"""
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

import sidecars
import structure

_SLUG = re.compile(r"https?://github\.com/([^/]+/[^/]+?)(?:\.git)?/?$")


def label_of(source):
    """owner/repo for a GitHub URL, the URL itself for anything else."""
    m = _SLUG.match(source)
    return m.group(1) if m else source


def check(items, resolver):
    """One record per current pin of the given items (see sidecars.read):

      local, source, commit, path, adopted_as, license, track,
      target, target_note, state

    target is the comparison target's sha, None when it could not be found,
    and target_note says which kind it is ("release v1.2.3", "<marketplace>
    pin") or why it is missing. state is "current", "outdated", or
    "unreachable".
    """
    pins = []
    for item in items:
        for pin in item.current_pins():
            target, note = resolver.resolve(pin["source"], item.track, item.local)
            commit = pin.get("commit", "")
            if target is None:
                state = "unreachable"
            elif target.startswith(commit) or commit.startswith(target):
                state = "current"
            else:
                state = "outdated"
            pins.append({
                "local": item.local,
                "source": pin["source"],
                "commit": commit,
                "path": pin.get("path", ""),
                "adopted_as": pin.get("adopted-as", ""),
                "license": pin.get("license", ""),
                "track": item.track,
                "target": target,
                "target_note": note,
                "state": state,
            })
    return pins


def _sanitize(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")


def clone_name(source):
    """The directory name a source is cloned under. Two spellings of one
    GitHub repo (with or without .git) share it."""
    return _sanitize(label_of(source))


def investigate(pins, items, workdir):
    """A deep look at the outdated pins. Returns {"items": [...], "structure": [...]}.

    Each outdated source is cloned (blobless) under workdir/clones, where the
    clones stay for whoever reads the result next.

    "items" has one record per outdated pin: check()'s fields without state,
    plus
      status        "changed" when the tracked path's content differs between
                    pin and target, "pin-only" when it is identical, "error"
                    when it could not be compared (then "error" says why)
      commit_count  commits touching the path between pin and target
      item_dir      for a changed item, a directory holding log.txt and, for a
                    copied item, upstream.diff. None otherwise.

    "structure" has structure.changes() records with source, pin and target
    added. An entry appears once per source even when several pins see it.
    """
    outdated = [p for p in pins if p["state"] == "outdated"]
    clones_dir = os.path.join(workdir, "clones")
    items_dir = os.path.join(workdir, "items")
    os.makedirs(clones_dir, exist_ok=True)
    os.makedirs(items_dir, exist_ok=True)

    # The same repo may be referenced under several URL spellings (with or
    # without .git). They share one clone, keyed by the sanitized label.
    clone_dirs = {p["source"]: os.path.join(clones_dir, clone_name(p["source"])) for p in outdated}
    to_clone = {}
    for src, d in clone_dirs.items():
        to_clone.setdefault(d, src)

    def clone(src):
        try:
            subprocess.run(
                ["git", "clone", "--filter=blob:none", "--no-checkout", "--quiet", src, clone_dirs[src]],
                check=True, capture_output=True, text=True, timeout=600)
            return src, None
        except subprocess.TimeoutExpired:
            return src, "clone timed out"
        except subprocess.CalledProcessError as e:
            return src, (e.stderr or "clone failed").strip().splitlines()[-1]

    clone_errors = {}  # clone dir -> error
    if to_clone:
        with ThreadPoolExecutor(max_workers=min(8, len(to_clone))) as pool:
            for src, err in pool.map(clone, to_clone.values()):
                if err:
                    clone_errors[clone_dirs[src]] = err

    def git(src, *args, timeout=120):
        return subprocess.run(["git", "-C", clone_dirs[src], *args],
                              capture_output=True, text=True, timeout=timeout)

    def object_at(src, sha, path):
        """Tree or blob sha of path at sha, or None if absent. Trees are present
        in a blobless clone, so this never fetches file contents."""
        spec = f"{sha}^{{tree}}" if path == "." else f"{sha}:{path}"
        res = git(src, "rev-parse", "--verify", "--quiet", spec)
        return res.stdout.strip() if res.returncode == 0 else None

    records = []
    for pin in sorted(outdated, key=lambda p: (p["source"], p["local"])):
        src, target = pin["source"], pin["target"]
        rec = {k: v for k, v in pin.items() if k != "state"}
        rec.update(status=None, commit_count=0, item_dir=None)
        records.append(rec)
        if clone_dirs[src] in clone_errors:
            rec.update(status="error", error=clone_errors[clone_dirs[src]])
            continue

        path = pin["path"] or "."
        log = git(src, "log", "--oneline", f"{pin['commit']}..{target}", "--", path)
        if log.returncode != 0:
            rec.update(status="error", error=(log.stderr or "git log failed").strip().splitlines()[-1])
            continue
        lines = [l for l in log.stdout.splitlines() if l.strip()]
        rec["commit_count"] = len(lines)

        # Decide by content, not history. When the pin is off the target's
        # ancestry (a release tag cut on a side branch), `pin..target` lists
        # commits even if the path ended up identical, and misses changes that
        # exist only on the pin's side. Fall back to the log when the path is
        # absent at either end.
        old_obj, new_obj = object_at(src, pin["commit"], path), object_at(src, target, path)
        unchanged = (old_obj == new_obj) if (old_obj and new_obj) else not lines
        if unchanged:
            rec["status"] = "pin-only"
            continue

        if not lines:
            # Content differs but pin..target is empty: the pin is on a side
            # branch. Show both sides (< pin-only, > target-only).
            log = git(src, "log", "--oneline", "--left-right", f"{pin['commit']}...{target}", "--", path)
            lines = [l for l in log.stdout.splitlines() if l.strip()]
            rec["commit_count"] = len(lines)

        rec["status"] = "changed"
        item_dir = os.path.join(items_dir, _sanitize(pin["local"]))
        os.makedirs(item_dir, exist_ok=True)
        rec["item_dir"] = item_dir
        with open(os.path.join(item_dir, "log.txt"), "w", encoding="utf-8") as f:
            f.write(log.stdout)
        # An upstream diff only for copied items. For an inspired-by item, and
        # for a whole-repo path, the log is the useful signal and a diff of "."
        # would be huge.
        if pin["adopted_as"] == "copied" and path != ".":
            diff = git(src, "diff", pin["commit"], target, "--", path, timeout=300)
            if diff.returncode == 0 and diff.stdout:
                with open(os.path.join(item_dir, "upstream.diff"), "w", encoding="utf-8") as f:
                    f.write(diff.stdout)

    # One structure scan per (source, pin, target): the paths moving together
    # share a comparison. A whole-repo item has no siblings to scan.
    structure_records = []
    scan_keys = sorted({(p["source"], p["commit"], p["target"]) for p in outdated
                        if p["path"] and p["path"] != "."})
    seen = {}  # normalized source -> {"added": set, "removed": set}
    for src, commit, target in scan_keys:
        if clone_dirs[src] in clone_errors:
            continue
        moving = sorted({p["path"] for p in outdated
                         if p["source"] == src and p["commit"] == commit and p["target"] == target})
        tracked = sidecars.tracked_paths(items, src)
        said = seen.setdefault(sidecars.normalize(src), {"added": set(), "removed": set()})
        for rec in structure.changes(lambda *a, src=src: git(src, *a, timeout=300),
                                     commit, target, moving, tracked):
            added = [p for p in rec["added"] if p not in said["added"]]
            removed = [p for p in rec["removed"] if p not in said["removed"]]
            said["added"].update(added)
            said["removed"].update(removed)
            if not added and not removed:
                continue
            structure_records.append({
                "source": src, "pin": commit, "target": target,
                "root": rec["root"], "scope": rec["scope"],
                "added": added, "removed": removed,
                "removed_tracked": [p for p in rec["removed_tracked"] if p in removed],
            })

    return {"items": records, "structure": structure_records}
