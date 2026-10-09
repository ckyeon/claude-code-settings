"""Tests for lib/targets.py: where an item's pin is measured against."""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
sys.path.insert(0, HERE)
import targets
import upstream


class TargetsCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = self._tmp.name
        self.root = os.path.join(self.tmp, "repo")
        os.makedirs(os.path.join(self.root, "user", "shared"))

    def repo(self, name):
        return upstream.Repo(os.path.join(self.tmp, name))

    def settings(self, data):
        with open(os.path.join(self.root, "user", "shared", "settings.json"), "w") as f:
            json.dump(data, f)

    def declare_plugin(self, name):
        os.makedirs(os.path.join(self.root, "user", "shared", "plugins", name))


class Head(TargetsCase):
    def test_untracked_item_is_measured_against_upstream_head(self):
        up = self.repo("up")
        up.put("a", "1")
        up.commit("one")
        tip = up.commit("two")
        self.assertEqual(targets.Targets(self.root).resolve(up.url(), "", "skills/a"), (tip, ""))

    def test_unreachable_source_has_no_target(self):
        sha, _note = targets.Targets(self.root).resolve("file:///nonexistent/repo", "", "skills/a")
        self.assertIsNone(sha)


class Release(TargetsCase):
    def test_newest_stable_tag_wins_and_head_is_ignored(self):
        up = self.repo("up")
        up.put("a", "1")
        up.commit("one", tag="v0.9.0")
        released = up.commit("two", tag="v0.10.0")
        up.commit("three", tag="v0.11.0-rc1")
        up.commit("unreleased")
        self.assertEqual(targets.Targets(self.root).resolve(up.url(), "release", "skills/a"),
                         (released, "release v0.10.0"))

    def test_annotated_tag_resolves_to_its_commit(self):
        up = self.repo("up")
        up.put("a", "1")
        commit = up.commit("one")
        up.git("tag", "-a", "v1.0.0", "-m", "release")
        sha, note = targets.Targets(self.root).resolve(up.url(), "release", "skills/a")
        self.assertEqual((sha, note), (commit, "release v1.0.0"))

    def test_source_without_a_stable_tag_has_no_target(self):
        up = self.repo("up")
        up.put("a", "1")
        up.commit("one")
        self.assertEqual(targets.Targets(self.root).resolve(up.url(), "release", "skills/a"),
                         (None, "no stable release tag"))


class Marketplace(TargetsCase):
    def marketplace(self, plugins):
        market = self.repo("market")
        market.put(".claude-plugin/marketplace.json", json.dumps({"plugins": plugins}))
        market.commit("list")
        return market

    def test_target_is_the_sha_the_marketplace_pins(self):
        market = self.marketplace([{"name": "p", "source": {"sha": "a" * 40}}])
        self.declare_plugin("p")
        self.settings({"enabledPlugins": {"p@official": True}})
        resolver = targets.Targets(self.root, builtin_marketplaces={"official": market.url()})
        self.assertEqual(resolver.resolve("https://x/p", "marketplace", "user/shared/plugins/p"),
                         ("a" * 40, "official pin"))

    def test_third_party_marketplace_is_read_from_its_declared_url(self):
        market = self.marketplace([{"name": "p", "source": {"sha": "b" * 40}}])
        self.declare_plugin("p")
        self.settings({"enabledPlugins": {"p@other": True},
                       "extraKnownMarketplaces": {"other": {"source": {"url": market.url()}}}})
        resolver = targets.Targets(self.root, builtin_marketplaces={})
        self.assertEqual(resolver.resolve("https://x/p", "marketplace", "user/shared/plugins/p"),
                         ("b" * 40, "other pin"))

    def test_each_way_the_pin_can_be_missing_is_named(self):
        market = self.marketplace([{"name": "unpinned", "source": "./plugins/unpinned"}])
        for name in ("unpinned", "absent", "nowhere"):
            self.declare_plugin(name)
        self.settings({"enabledPlugins": {"unpinned@official": True, "absent@official": True}})
        resolver = targets.Targets(self.root, builtin_marketplaces={"official": market.url()})
        reason = lambda name: resolver.resolve("https://x/p", "marketplace", f"user/shared/plugins/{name}")
        self.assertEqual(reason("unpinned"), (None, "official does not pin a sha for unpinned"))
        self.assertEqual(reason("absent"), (None, "absent not listed in official"))
        self.assertEqual(reason("nowhere"), (None, "marketplace unknown (not in any enabledPlugins)"))


class UnknownTrack(TargetsCase):
    def test_unknown_track_never_falls_back_to_head(self):
        self.assertEqual(targets.Targets(self.root).resolve("https://x/p", "nightly", "skills/a"),
                         (None, "unknown track 'nightly'"))


if __name__ == "__main__":
    unittest.main()
