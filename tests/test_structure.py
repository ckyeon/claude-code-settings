"""Tests for lib/structure.py: what changed upstream between two commits."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
sys.path.insert(0, HERE)
import structure
import upstream


class StandardUpstream(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.repo, cls.c = upstream.build(os.path.join(cls._tmp.name, "up"))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def changes(self, old, new, moving, tracked):
        return structure.changes(self.repo.git, self.c[old], self.c[new], moving, tracked)

    def by_scope(self, records):
        return {r["scope"]: r for r in records}

    def test_sibling_pass_lists_what_appeared_and_vanished_next_to_a_moving_path(self):
        rec = self.by_scope(self.changes("c1", "c2", ["skills/eng/a"], {"skills/eng/a"}))["sibling"]
        self.assertEqual(rec["root"], "skills/eng")
        self.assertEqual(rec["added"], ["skills/eng/c"])
        self.assertEqual(rec["removed"], ["skills/eng/r"])

    def test_a_removed_entry_is_flagged_only_when_this_repo_tracks_it(self):
        untracked = self.by_scope(self.changes("c1", "c2", ["skills/eng/a"], {"skills/eng/a"}))
        tracked = self.by_scope(self.changes("c1", "c2", ["skills/eng/a"], {"skills/eng/a", "skills/eng/r"}))
        self.assertEqual(untracked["sibling"]["removed_tracked"], [])
        self.assertEqual(tracked["sibling"]["removed_tracked"], ["skills/eng/r"])

    def test_elsewhere_pass_reports_new_skills_and_plugins_outside_the_tracked_dirs(self):
        rec = self.by_scope(self.changes("c1", "c2", ["skills/eng/a"], {"skills/eng/a"}))["elsewhere"]
        self.assertEqual(rec["added"], ["docs/ünï", "plugins/p2", "skills/beta/new", "skills/prod/q"])

    def test_a_new_plugin_is_one_entry_and_its_nested_skill_is_folded_in(self):
        added = self.by_scope(self.changes("c1", "c2", ["skills/eng/a"], {"skills/eng/a"}))["elsewhere"]["added"]
        self.assertIn("plugins/p2", added)
        self.assertNotIn("plugins/p2/skills/x", added)

    def test_additions_inside_existing_units_are_left_out(self):
        added = self.by_scope(self.changes("c1", "c2", ["skills/eng/a"], {"skills/eng/a"}))["elsewhere"]["added"]
        self.assertNotIn("plugins/p1/skills/s2", added)   # inside an existing plugin
        self.assertNotIn("skills/eng/a/sub", added)       # inside a tracked path
        self.assertNotIn("skills/eng/b/deep", added)      # nested in an unadopted skill

    def test_entries_that_predate_the_old_commit_never_appear(self):
        everything = [p for r in self.changes("c1", "c2", ["skills/eng/a"], {"skills/eng/a"}) for p in r["added"]]
        self.assertNotIn("skills/beta/old", everything)
        self.assertNotIn("skills/eng/b", everything)

    def test_a_sibling_of_a_path_tracked_at_another_pin_is_left_to_that_pin(self):
        # skills/prod/p is tracked but not moving here, so skills/prod is a
        # tracked dir whose own pin decides when skills/prod/q is reported.
        added = self.by_scope(self.changes("c1", "c2", ["skills/eng/a"],
                                           {"skills/eng/a", "skills/prod/p"}))["elsewhere"]["added"]
        self.assertNotIn("skills/prod/q", added)

    def test_two_moving_dirs_each_get_a_sibling_record(self):
        records = self.changes("c1", "c2", ["skills/eng/a", "skills/prod/p"],
                               {"skills/eng/a", "skills/prod/p"})
        roots = sorted(r["root"] for r in records if r["scope"] == "sibling")
        self.assertEqual(roots, ["skills/eng", "skills/prod"])

    def test_no_structural_change_gives_no_records(self):
        self.assertEqual(self.changes("c2", "c3", ["skills/eng/a"], {"skills/eng/a"}), [])

    def test_a_whole_repo_path_has_no_siblings(self):
        self.assertEqual(self.changes("c1", "c2", ["."], set()), [])

    def test_an_unlistable_commit_is_skipped_not_reported_as_empty(self):
        records = structure.changes(self.repo.git, "0" * 40, self.c["c2"], ["skills/eng/a"], {"skills/eng/a"})
        self.assertEqual(records, [])


class TopLevelTrackedPath(unittest.TestCase):
    def test_new_top_level_entries_are_siblings_and_deeper_ones_are_elsewhere(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = upstream.Repo(os.path.join(tmp, "up"))
            repo.plugin("plug")
            repo.put("pkg/readme.md", "x")
            old = repo.commit("old")
            repo.plugin("other")
            repo.skill("pkg/deep/x")
            new = repo.commit("new")
            records = {r["scope"]: r for r in structure.changes(repo.git, old, new, ["plug"], {"plug"})}
        self.assertEqual(records["sibling"]["root"], ".")
        self.assertEqual(records["sibling"]["added"], ["other"])
        self.assertEqual(records["elsewhere"]["added"], ["pkg/deep/x"])


if __name__ == "__main__":
    unittest.main()
