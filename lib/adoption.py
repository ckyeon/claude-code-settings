"""Bringing upstream content into the repo and moving its pin.

bin/adopt records an item for the first time. bin/re-pin moves the pin of
items already recorded. Both go through here: one clone per source, the same
copy and prune, the same sidecar entry, the same structure warning.
"""
import datetime
import hashlib
import os
import shutil
import subprocess
import tempfile

import sidecars
import structure


class AdoptionError(Exception):
    """Something about one item or source that stops it from being adopted."""


class Upstream:
    """A blobless, no-checkout clone of one source, made once and reused."""

    def __init__(self, source):
        self.source = source
        self._tmp = tempfile.mkdtemp(prefix="adoption-")
        self.dir = os.path.join(self._tmp, "clone")
        res = subprocess.run(
            ["git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", source, self.dir],
            capture_output=True, text=True)
        if res.returncode != 0:
            self.close()
            raise AdoptionError(f"failed to clone {source}")

    def close(self):
        shutil.rmtree(self._tmp, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def git(self, *args):
        return subprocess.run(["git", "-C", self.dir, *args], capture_output=True, text=True)

    def resolve(self, rev):
        """The full commit sha for rev, or None when the source does not have it."""
        res = self.git("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
        return res.stdout.strip() if res.returncode == 0 else None

    def has(self, sha, path):
        return path == "." or self.git("cat-file", "-e", f"{sha}:{path}").returncode == 0

    def blobs(self, sha, path):
        """{relative path: blob sha} for path at sha, or None when sha is unknown.

        A file maps the empty string to its blob. Only trees are read.
        """
        if self.resolve(sha) is None:
            return None
        spec = [] if path == "." else ["--", path]
        res = self.git("ls-tree", "-r", "-z", sha, *spec)
        if res.returncode != 0:
            return None
        prefix = "" if path == "." else path.rstrip("/") + "/"
        found = {}
        for record in res.stdout.split("\0"):
            if not record:
                continue
            meta, _, name = record.partition("\t")
            kind, blob = meta.split()[1:3]
            if kind != "blob":
                continue
            found["" if name == path else name[len(prefix):]] = blob
        return found

    def checkout(self, sha, paths):
        """Put paths at sha into the clone's working tree, fetching only their blobs."""
        if "." in paths:
            self.git("sparse-checkout", "disable")
        else:
            self.git("sparse-checkout", "init", "--cone")
            self.git("sparse-checkout", "set", *paths)
        res = self.git("checkout", "--quiet", sha)
        if res.returncode != 0:
            raise AdoptionError(f"could not check out {sha[:8]} of {self.source}")


def _blob_sha(data, digest_size):
    h = hashlib.sha256() if digest_size == 64 else hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def _local_files(dest):
    """Relative paths of the files that make up the local copy at dest.

    Files git ignores (.DS_Store and the like) are not part of the copy. The
    item's own sidecar is not either.
    """
    if not os.path.isdir(dest):
        return [""]
    listed = subprocess.run(
        ["git", "-C", dest, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True)
    if listed.returncode == 0:
        names = [n for n in listed.stdout.split("\0") if n and os.path.lexists(os.path.join(dest, n))]
    else:  # not inside a git repository
        names = [os.path.relpath(os.path.join(root, f), dest)
                 for root, _dirs, files in os.walk(dest) for f in files]
    return sorted(n for n in names if n != sidecars.SUFFIX)


def local_drift(upstream, sha, path, dest):
    """How the local copy at dest differs from path at sha.

    Returns a list of differences, empty when the copy is exactly what upstream
    had, or None when sha is not in the source and nothing can be compared.
    """
    theirs = upstream.blobs(sha, path)
    if theirs is None:
        return None
    digest_size = len(next(iter(theirs.values()))) if theirs else 40
    ours = {}
    for rel in _local_files(dest):
        full = os.path.join(dest, rel) if rel else dest
        if not os.path.lexists(full):
            continue
        if os.path.islink(full):
            data = os.readlink(full).encode()
        else:
            with open(full, "rb") as f:
                data = f.read()
        ours[rel] = _blob_sha(data, digest_size)
    label = lambda rel: rel or os.path.basename(dest)
    drift = [f"changed locally: {label(r)}" for r in sorted(ours) if r in theirs and ours[r] != theirs[r]]
    drift += [f"added locally: {label(r)}" for r in sorted(ours) if r not in theirs]
    drift += [f"deleted locally: {label(r)}" for r in sorted(theirs) if r not in ours]
    return drift


def copy_in(upstream, path, dest):
    """Replace dest with path from the clone's working tree (see Upstream.checkout).

    A folder that already has a sidecar is emptied first, keeping the sidecar,
    so files upstream deleted do not linger. The sidecar gate means a mistyped
    destination can never wipe a directory this repo does not own. Returns
    "folder" or "file", and whether the destination was pruned.
    """
    src = upstream.dir if path == "." else os.path.join(upstream.dir, path)
    if not os.path.lexists(src):
        raise AdoptionError(f"path '{path}' not found in {upstream.source}")
    parent = os.path.dirname(dest)
    if parent:
        os.makedirs(parent, exist_ok=True)
    if not os.path.isdir(src):
        shutil.copy2(src, dest)
        return "file", False
    pruned = os.path.isfile(os.path.join(dest, sidecars.SUFFIX))
    if pruned:
        for name in os.listdir(dest):
            if name == sidecars.SUFFIX:
                continue
            victim = os.path.join(dest, name)
            if os.path.isdir(victim) and not os.path.islink(victim):
                shutil.rmtree(victim)
            else:
                os.remove(victim)
    shutil.copytree(src, dest, symlinks=True, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".git"))
    return "folder", pruned


def record(dest, source, sha, path, license, mode, notes=""):
    """Append the new pin to dest's sidecar. Returns the sidecar's path."""
    sidecar = sidecars.sidecar_path(dest)
    today = datetime.date.today().isoformat()
    sidecars.append(sidecar, sidecars.new_entry(source, sha, path, license, mode, today, notes))
    return sidecar


def structure_lines(records):
    """The lines a tool prints for structure.changes() records."""
    lines = []
    for rec in records:
        mark = "  (outside tracked dirs)" if rec["scope"] == "elsewhere" else ""
        lines += [f"NEW      {p}{mark}" for p in rec["added"]]
    for rec in records:
        for p in rec["removed"]:
            mark = "  ** adopted here **" if p in rec["removed_tracked"] else ""
            lines.append(f"REMOVED  {p}{mark}")
    return lines


class Result:
    """What happened to one item in a re-pin: moved, current, or failed."""

    def __init__(self, local, status, detail=""):
        self.local = local
        self.status = status
        self.detail = detail


def re_pin(repo_root, locals_, resolver, commit=None, notes="", overwrite_local=False, say=print):
    """Move the pin of each item in locals_ to its comparison target, or to commit.

    Items are grouped by source so each source is cloned once and its structure
    changes are reported once. One item failing does not stop the others.
    Returns a Result per requested item. say(line) receives progress output.
    """
    items, _unreadable = sidecars.read(repo_root)
    by_local = {item.local: item for item in items}

    results = {}   # local -> Result, for items settled before any clone
    moves = []     # (item, pin)
    for local in locals_:
        item = by_local.get(local)
        if item is None:
            results[local] = Result(local, "failed", "has no sidecar; use bin/adopt to adopt it first")
            continue
        pins = item.current_pins()
        if not pins:
            results[local] = Result(local, "failed", "has diverged from upstream (its newest record is \"self\")")
            continue
        moves += [(item, pin) for pin in pins]

    if commit:
        sources = {sidecars.normalize(pin["source"]) for _item, pin in moves}
        if len(sources) > 1:
            raise AdoptionError("--commit names one commit, but the items come from "
                                f"{len(sources)} sources; re-pin them one source at a time")

    by_source = {}
    for item, pin in moves:
        by_source.setdefault(sidecars.normalize(pin["source"]), []).append((item, pin))

    for _key, group in by_source.items():
        source = group[0][1]["source"]
        try:
            upstream = Upstream(source)
        except AdoptionError as e:
            for item, _pin in group:
                results[item.local] = Result(item.local, "failed", str(e))
            continue
        with upstream:
            _re_pin_source(repo_root, upstream, group, items, resolver, commit, notes,
                           overwrite_local, say, results)

    return [results[local] for local in locals_]


def _re_pin_source(repo_root, upstream, group, items, resolver, commit, notes,
                   overwrite_local, say, results):
    source = upstream.source
    tracked = sidecars.tracked_paths(items, source)

    # Where each pin is headed.
    planned = {}   # (old sha, new sha) -> [(item, pin)]
    for item, pin in group:
        if commit:
            wanted, why = commit, ""
        else:
            wanted, why = resolver.resolve(source, item.track, item.local)
        if not wanted:
            results[item.local] = Result(item.local, "failed",
                                         f"comparison target not found ({why or 'source unreachable'})")
            continue
        new = upstream.resolve(wanted)
        if new is None:
            results[item.local] = Result(item.local, "failed", f"commit {wanted[:12]} not found in {source}")
            continue
        old = pin.get("commit", "")
        if new.startswith(old) or old.startswith(new):
            results[item.local] = Result(item.local, "current", f"already at {new[:8]}")
            continue
        planned.setdefault((old, new), []).append((item, pin))

    for (old, new), batch in planned.items():
        say("")
        say(f"{source}  {old[:8]} → {new[:8]}")
        if upstream.resolve(old):
            moving = [pin["path"] for _item, pin in batch]
            for line in structure_lines(structure.changes(upstream.git, old, new, moving, tracked)):
                say(f"  ⚠ {line}")

        # Decide what can move before touching anything.
        ready = []
        for item, pin in batch:
            path, dest = pin["path"], os.path.join(repo_root, item.local)
            if not upstream.has(new, path):
                results[item.local] = Result(item.local, "failed",
                                             f"'{path}' no longer exists upstream at {new[:8]}")
                continue
            if pin.get("adopted-as") == "copied" and not overwrite_local:
                drift = local_drift(upstream, old, path, dest)
                if drift is None:
                    results[item.local] = Result(
                        item.local, "failed",
                        f"cannot compare the local copy: the old pin {old[:8]} is not in the source "
                        "(pass --overwrite-local to replace it anyway)")
                    continue
                if drift:
                    shown = "; ".join(drift[:5]) + (f"; and {len(drift) - 5} more" if len(drift) > 5 else "")
                    results[item.local] = Result(
                        item.local, "failed",
                        f"the local copy differs from the old pin ({shown}). "
                        "Pass --overwrite-local to replace it anyway")
                    continue
            ready.append((item, pin))

        copied = [pin["path"] for _item, pin in ready if pin.get("adopted-as") == "copied"]
        if copied:
            try:
                upstream.checkout(new, copied)
            except AdoptionError as e:
                for item, pin in ready:
                    if pin.get("adopted-as") == "copied":
                        results[item.local] = Result(item.local, "failed", str(e))
                ready = [(i, p) for i, p in ready if p.get("adopted-as") != "copied"]

        for item, pin in ready:
            dest = os.path.join(repo_root, item.local)
            try:
                if pin.get("adopted-as") == "copied":
                    copy_in(upstream, pin["path"], dest)
                record(dest, pin["source"], new, pin["path"], pin.get("license", ""),
                       pin.get("adopted-as", ""), notes)
            except (AdoptionError, OSError, ValueError) as e:
                results[item.local] = Result(item.local, "failed", str(e))
                continue
            results[item.local] = Result(item.local, "moved", f"{old[:8]} → {new[:8]}")
