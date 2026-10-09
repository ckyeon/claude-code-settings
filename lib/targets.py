"""Comparison targets: the upstream point an item's pin is measured against.

Usually upstream HEAD. An item whose sidecar sets "track" is measured against
the source's newest stable release, or against the commit its marketplace pins
(ADR 0065). bin/check-updates asks this to decide whether a pin is behind, and
bin/re-pin asks it to decide where a pin moves to, so the two always agree.
"""
import json
import os
import re
import subprocess
import tempfile

import declarations

STABLE_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
# Built-in marketplaces have no extraKnownMarketplaces entry to read a repo from.
BUILTIN_MARKETPLACES = {
    "claude-plugins-official": "https://github.com/anthropics/claude-plugins-official",
}


class Targets:
    """Resolves comparison targets, asking each upstream at most once.

    builtin_marketplaces maps a built-in marketplace name to its repo URL. It
    defaults to the real ones and exists so tests can point at a local repo.
    """

    def __init__(self, repo_root, builtin_marketplaces=None):
        self.repo_root = repo_root
        self.builtin = BUILTIN_MARKETPLACES if builtin_marketplaces is None else builtin_marketplaces
        self._heads = {}
        self._releases = {}
        self._pins = {}
        self._marketplace_json = {}
        self._plugin_marketplaces = None

    def resolve(self, source, track, local):
        """(sha, note) for an item, or (None, reason) when the target cannot be found.

        A failed lookup never falls back to HEAD: that would report an item
        pinned off HEAD on purpose as outdated, or move its pin to the wrong place.
        """
        if not track:
            return self.head(source), ""
        if track == "release":
            if source not in self._releases:
                self._releases[source] = self._latest_release(source)
            return self._releases[source]
        if track == "marketplace":
            name = os.path.basename(local)
            if name not in self._pins:
                self._pins[name] = self._marketplace_pin(name)
            return self._pins[name]
        return None, f"unknown track {track!r}"

    def head(self, source):
        """Upstream HEAD of a source, or None when it cannot be reached."""
        if source not in self._heads:
            try:
                out = subprocess.check_output(
                    ["git", "ls-remote", source, "HEAD"],
                    stderr=subprocess.DEVNULL, text=True, timeout=30)
                match = re.match(r"([0-9a-f]{40})\s", out)
                self._heads[source] = match.group(1) if match else None
            except Exception:
                self._heads[source] = None
        return self._heads[source]

    def _latest_release(self, source):
        try:
            out = subprocess.check_output(
                ["git", "ls-remote", "--tags", source],
                stderr=subprocess.DEVNULL, text=True, timeout=30)
        except Exception:
            return None, "tag lookup failed"
        tags = {}  # tag name -> commit sha. For annotated tags the peeled ^{} line wins.
        for line in out.splitlines():
            sha, _, ref = line.partition("\t")
            name = ref[len("refs/tags/"):]
            peeled = name.endswith("^{}")
            if peeled:
                name = name[:-3]
            if STABLE_TAG.match(name) and (peeled or name not in tags):
                tags[name] = sha
        if not tags:
            return None, "no stable release tag"
        best = max(tags, key=lambda n: tuple(int(x) for x in STABLE_TAG.match(n).groups()))
        return tags[best], f"release {best}"

    def _marketplace_pin(self, name):
        if self._plugin_marketplaces is None:
            # Same resolution install.sh uses: enabledPlugins + extraKnownMarketplaces.
            self._plugin_marketplaces = {row[0]: (row[1], row[2])
                                         for row in declarations.plugin_rows(self.repo_root)}
        market, repo = self._plugin_marketplaces.get(name, ("", ""))
        if not market:
            return None, "marketplace unknown (not in any enabledPlugins)"
        url = self.builtin.get(market) or (
            repo if "://" in repo else f"https://github.com/{repo}" if repo else "")
        if not url:
            return None, f"no repo known for marketplace {market}"
        if url not in self._marketplace_json:
            self._marketplace_json[url] = self._read_marketplace(url)
        data = self._marketplace_json[url]
        if data is None:
            return None, f"could not read {market} marketplace.json"
        for plugin in data.get("plugins", []):
            if plugin.get("name") == name:
                source = plugin.get("source")
                if isinstance(source, dict) and source.get("sha"):
                    return source["sha"], f"{market} pin"
                return None, f"{market} does not pin a sha for {name}"
        return None, f"{name} not listed in {market}"

    @staticmethod
    def _read_marketplace(url):
        try:
            with tempfile.TemporaryDirectory() as tmp:
                clone = subprocess.run(
                    ["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout",
                     "--quiet", url, tmp],
                    capture_output=True, text=True, timeout=120)
                if clone.returncode != 0:
                    return None
                show = subprocess.run(
                    ["git", "-C", tmp, "show", "HEAD:.claude-plugin/marketplace.json"],
                    capture_output=True, text=True, timeout=60)
                return json.loads(show.stdout) if show.returncode == 0 else None
        except (subprocess.TimeoutExpired, ValueError):
            return None
