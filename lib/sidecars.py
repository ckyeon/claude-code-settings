"""Sidecars: the provenance record of each item.

The one place that knows where sidecars live, which item each describes, what
an item's current pins and tracked paths are, how an entry is appended, and
what makes a sidecar valid. The schema is documented in docs/PROVENANCE.md.
"""
import json
import os
import re

SUFFIX = ".provenance.json"
REQUIRED = ("source", "commit", "path", "license", "adopted-as")
# Top-level keys some tool reads. Anything else is ignored everywhere, so a
# misspelled "track" would silently compare against HEAD again (ADR 0066).
TOP_LEVEL_KEYS = ("provenance", "track")
TRACKS = ("release", "marketplace")
MODES = ("copied", "inspired-by")
SKIP_DIRS = (".git", "node_modules")


def normalize(url):
    """A source URL without the trailing slash or .git, so two spellings match."""
    return re.sub(r"\.git$", "", (url or "").rstrip("/"))


def current_pins(entries):
    """The newest entry of each source, in the order the sources first appear.

    Empty when the newest entry overall is "self": the item has diverged from
    upstream and is no longer tracked.
    """
    usable = [e for e in entries if isinstance(e, dict)]
    if not usable or usable[-1].get("source") == "self":
        return []
    newest = {}
    for entry in usable:
        source = entry.get("source")
        if source and source != "self":
            newest[normalize(source)] = entry
    return list(newest.values())


class Item:
    """One item and the sidecar that records its provenance.

    local and sidecar are paths relative to the repo root.
    """

    def __init__(self, local, sidecar, entries, track):
        self.local = local
        self.sidecar = sidecar
        self.entries = entries
        self.track = track

    def current_pins(self):
        return current_pins(self.entries)

    def pin_for(self, source):
        """The current pin for one source, or None."""
        want = normalize(source)
        for entry in self.current_pins():
            if normalize(entry.get("source")) == want:
                return entry
        return None


def sidecar_path(dest):
    """Where the sidecar of the item at dest lives: inside a folder, beside a file."""
    return os.path.join(dest, SUFFIX) if os.path.isdir(dest) else dest + SUFFIX


def _sidecar_files(repo_root):
    found = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        found += [os.path.join(root, name) for name in files if name.endswith(SUFFIX)]
    return sorted(found)


def _local_of(rel):
    if os.path.basename(rel) == SUFFIX:
        return os.path.dirname(rel)      # a folder's sidecar sits inside it
    return rel[: -len(SUFFIX)]           # a file's sidecar sits beside it


def _load(path):
    """(data, None) when the file holds a provenance list, else (None, reason)."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        return None, f"invalid JSON: {e}"
    if not isinstance(data, dict) or not isinstance(data.get("provenance"), list):
        return None, "provenance[] missing or not a list"
    return data, None


def read(repo_root):
    """(items, unreadable) for every sidecar in the repo, ordered by path.

    unreadable is [(sidecar path, reason)] for files that are not valid JSON or
    hold no provenance list. Their items are left out rather than guessed at.
    """
    items, unreadable = [], []
    for path in _sidecar_files(repo_root):
        rel = os.path.relpath(path, repo_root)
        data, reason = _load(path)
        if reason:
            unreadable.append((rel, reason))
            continue
        items.append(Item(_local_of(rel), rel, data["provenance"], data.get("track") or ""))
    return items, unreadable


def tracked_paths(items, source):
    """Upstream paths the repo tracks from one source: its current pins' paths.

    A whole-repo pin (path ".") tracks no particular path and is left out.
    """
    want = normalize(source)
    return {
        entry["path"]
        for item in items
        for entry in item.current_pins()
        if normalize(entry.get("source")) == want and entry.get("path") and entry["path"] != "."
    }


def new_entry(source, commit, path, license, mode, adopted_at, notes=""):
    entry = {
        "source": source,
        "commit": commit,
        "path": path,
        "license": license,
        "adopted-as": mode,
        "adopted-at": adopted_at,
    }
    if notes:
        entry["notes"] = notes
    return entry


def append(path, entry):
    """Append an entry to the sidecar at path, creating the file if needed.

    Top-level keys such as "track" are kept. Raises ValueError when an existing
    file is not a sidecar, rather than overwriting it.
    """
    if os.path.exists(path):
        data, reason = _load(path)
        if reason:
            raise ValueError(f"malformed sidecar at {path} ({reason})")
    else:
        data = {"provenance": []}
    data["provenance"].append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def validate(repo_root):
    """[(sidecar path, problem)] for every schema breach in the repo's sidecars."""
    problems = []
    for path in _sidecar_files(repo_root):
        rel = os.path.relpath(path, repo_root)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            problems.append((rel, f"invalid JSON: {e}"))
            continue
        prov = data.get("provenance") if isinstance(data, dict) else None
        if not isinstance(prov, list) or not prov:
            problems.append((rel, "provenance[] missing or empty"))
            continue
        unknown = sorted(k for k in data if k not in TOP_LEVEL_KEYS)
        if unknown:
            problems.append((rel, f"unknown top-level key(s): {', '.join(unknown)}"))
        if "track" in data and data["track"] not in TRACKS:
            problems.append((rel, f"track {data['track']!r} is not one of: {', '.join(TRACKS)}"))
        for idx, entry in enumerate(prov):
            # `source: "self"` marks a deliberate divergence from upstream: the
            # content is now ours, so there is no commit, path, or license to pin.
            required = ("source", "adopted-as") if entry.get("source") == "self" else REQUIRED
            missing = [k for k in required if not entry.get(k)]
            if missing:
                problems.append((rel, f"provenance[{idx}] missing: {', '.join(missing)}"))
    return problems
