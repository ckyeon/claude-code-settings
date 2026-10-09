"""Tests for lib/updates.py: is a pin behind its target, and what moved upstream."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
sys.path.insert(0, HERE)
import sidecars
import targets
import updates
import upstream

SELF = {"source": "self", "adopted-as": "inspired-by", "adopted-at": "2026-01-01"}


class UpdatesCase(unittest.TestCase):
    """An empty local repo whose sidecars are written directly."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = self._tmp.name
        self.root = os.path.join(self.tmp, "repo")
        os.makedirs(self.root)

    def pin(self, local, source, commit, path, mode="copied", extra=()):
        """Record an item pinned at commit, without copying anything in."""
        os.makedirs(os.path.join(self.root, local), exist_ok=True)
        sidecar = os.path.join(self.root, local, ".provenance.json")
        sidecars.append(sidecar, sidecars.new_entry(source, commit, path, "MIT", mode, "2026-01-01"))
        for entry in extra:
            sidecars.append(sidecar, entry)

    def check(self):
        self.items, _ = sidecars.read(self.root)
        self.pins = updates.check(self.items, targets.Targets(self.root))
        return {p["local"]: p for p in self.pins}

    def investigate(self):
        self.check()
        self.workdir = os.path.join(self.tmp, "work")
        result = updates.investigate(self.pins, self.items, self.workdir)
        return {r["local"]: r for r in result["items"]}, result["structure"]


class StandardUpstream(UpdatesCase):
    @classmethod
    def setUpClass(cls):
        cls._up_tmp = tempfile.TemporaryDirectory()
        cls.up, cls.c = upstream.build(os.path.join(cls._up_tmp.name, "up"))

    @classmethod
    def tearDownClass(cls):
        cls._up_tmp.cleanup()

    def test_a_pin_is_current_outdated_or_unreachable(self):
        self.pin("a", self.up.url(), self.c["c1"], "skills/eng/a")
        self.pin("z", self.up.url(), self.c["c3"], "skills/eng/z")
        self.pin("gone", "file:///nonexistent/repo", "c" * 40, "x")
        pins = self.check()
        self.assertEqual({k: v["state"] for k, v in pins.items()},
                         {"a": "outdated", "z": "current", "gone": "unreachable"})
        self.assertEqual(pins["a"]["target"], self.c["c3"])
        self.assertIsNone(pins["gone"]["target"])

    def test_an_item_that_diverged_from_upstream_is_not_checked(self):
        self.pin("a", self.up.url(), self.c["c1"], "skills/eng/a", extra=[SELF])
        self.assertEqual(self.check(), {})

    def test_content_decides_between_changed_and_pin_only(self):
        self.pin("a", self.up.url(), self.c["c1"], "skills/eng/a")
        self.pin("z", self.up.url(), self.c["c1"], "skills/eng/z")
        records, _ = self.investigate()
        self.assertEqual((records["a"]["status"], records["z"]["status"]), ("changed", "pin-only"))
        self.assertEqual(records["a"]["commit_count"], 1)
        self.assertIsNone(records["z"]["item_dir"])

    def test_a_changed_copied_item_gets_a_log_and_a_diff(self):
        self.pin("a", self.up.url(), self.c["c1"], "skills/eng/a")
        records, _ = self.investigate()
        self.assertEqual(sorted(os.listdir(records["a"]["item_dir"])), ["log.txt", "upstream.diff"])

    def test_a_changed_inspired_by_item_gets_only_a_log(self):
        self.pin("a", self.up.url(), self.c["c1"], "skills/eng/a", mode="inspired-by")
        records, _ = self.investigate()
        self.assertEqual(os.listdir(records["a"]["item_dir"]), ["log.txt"])

    def test_a_pin_missing_from_upstream_is_an_error_not_a_guess(self):
        self.pin("a", self.up.url(), "d" * 40, "skills/eng/a")
        records, _ = self.investigate()
        self.assertEqual(records["a"]["status"], "error")
        self.assertTrue(records["a"]["error"])

    def test_records_carry_the_target_under_one_name(self):
        self.pin("a", self.up.url(), self.c["c1"], "skills/eng/a")
        records, structure_records = self.investigate()
        self.assertEqual(records["a"]["target"], self.c["c3"])
        self.assertNotIn("head", records["a"])
        self.assertNotIn("state", records["a"])
        self.assertEqual(structure_records[0]["target"], self.c["c3"])
        self.assertNotIn("head", structure_records[0])

    def test_structure_records_name_what_was_removed_and_tracked(self):
        self.pin("a", self.up.url(), self.c["c1"], "skills/eng/a")
        self.pin("r", self.up.url(), self.c["c1"], "skills/eng/r")
        _, structure_records = self.investigate()
        sibling = next(r for r in structure_records if r["scope"] == "sibling")
        self.assertEqual(sibling["removed_tracked"], ["skills/eng/r"])
        self.assertEqual(sibling["pin"], self.c["c1"])

    def test_only_outdated_pins_are_investigated(self):
        self.pin("a", self.up.url(), self.c["c1"], "skills/eng/a")
        self.pin("z", self.up.url(), self.c["c3"], "skills/eng/z")
        records, _ = self.investigate()
        self.assertEqual(sorted(records), ["a"])


class SideBranches(UpdatesCase):
    def build(self):
        up = upstream.Repo(os.path.join(self.tmp, "up"))
        up.skill("skills/a", "one")
        up.put("other.md", "x")
        return up, up.commit("base")

    def test_a_pin_on_a_side_branch_with_different_content_is_changed(self):
        up, _base = self.build()
        up.git("checkout", "-q", "-b", "side")
        up.skill("skills/a", "side edit")
        side = up.commit("side edit")
        up.git("checkout", "-q", "main")
        up.put("other.md", "y")
        up.commit("unrelated")
        self.pin("a", up.url(), side, "skills/a")
        records, _ = self.investigate()
        self.assertEqual(records["a"]["status"], "changed")
        self.assertGreaterEqual(records["a"]["commit_count"], 1)

    def test_same_content_reached_by_another_commit_is_pin_only(self):
        up, _base = self.build()
        up.git("checkout", "-q", "-b", "release")
        up.skill("skills/a", "two")
        tagged = up.commit("release edit")
        up.git("checkout", "-q", "main")
        up.skill("skills/a", "two")
        up.commit("same edit on main")
        self.pin("a", up.url(), tagged, "skills/a")
        records, _ = self.investigate()
        self.assertEqual(records["a"]["status"], "pin-only")


class StructureAcrossPins(UpdatesCase):
    def test_an_entry_seen_from_two_pins_is_reported_once(self):
        up = upstream.Repo(os.path.join(self.tmp, "up"))
        up.skill("skills/eng/a")
        up.skill("skills/prod/p")
        k1 = up.commit("k1")
        up.put("notes.md", "x")
        k2 = up.commit("k2")
        up.skill("docs/new")
        up.commit("k3")
        self.pin("a", up.url(), k1, "skills/eng/a")
        self.pin("p", up.url(), k2, "skills/prod/p")
        _, structure_records = self.investigate()
        reported = [p for r in structure_records for p in r["added"]]
        self.assertEqual(reported, ["docs/new"])


if __name__ == "__main__":
    unittest.main()
