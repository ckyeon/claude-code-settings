"""Tests for lib/adoption.py: copying upstream content in and moving pins."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
sys.path.insert(0, HERE)
import adoption
import sidecars
import targets
import upstream


class AdoptionCase(unittest.TestCase):
    """A standard upstream plus an empty local repo to adopt into."""

    @classmethod
    def setUpClass(cls):
        cls._up_tmp = tempfile.TemporaryDirectory()
        cls.up, cls.c = upstream.build(os.path.join(cls._up_tmp.name, "up"))
        cls.up.git("tag", "v1.0.0", cls.c["c2"])

    @classmethod
    def tearDownClass(cls):
        cls._up_tmp.cleanup()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = os.path.join(self._tmp.name, "repo")
        os.makedirs(self.root)
        subprocess.run(["git", "-C", self.root, "init", "-q"], check=True)
        self.write(".gitignore", ".DS_Store\n")
        self.said = []

    def write(self, rel, text):
        full = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def read(self, rel):
        with open(os.path.join(self.root, rel), encoding="utf-8") as f:
            return f.read()

    def entries(self, local):
        with open(sidecars.sidecar_path(os.path.join(self.root, local)), encoding="utf-8") as f:
            return json.load(f)["provenance"]

    def adopt(self, local, path, at="c1", mode="copied", track=None):
        """What bin/adopt does: copy the path in and record the pin."""
        dest = os.path.join(self.root, local)
        with adoption.Upstream(self.up.url()) as clone:
            if mode == "copied":
                clone.checkout(self.c[at], [path])
                adoption.copy_in(clone, path, dest)
            else:
                os.makedirs(dest, exist_ok=True)
            sidecar = adoption.record(dest, self.up.url(), self.c[at], path, "MIT", mode)
        if track:
            with open(sidecar, encoding="utf-8") as f:
                data = json.load(f)
            data["track"] = track
            with open(sidecar, "w", encoding="utf-8") as f:
                json.dump(data, f)

    def re_pin(self, *locals_, **kwargs):
        results = adoption.re_pin(self.root, list(locals_), targets.Targets(self.root),
                                  say=self.said.append, **kwargs)
        return {r.local: r for r in results}


class UpstreamClone(AdoptionCase):
    def test_resolve_expands_a_short_sha_and_rejects_an_unknown_one(self):
        with adoption.Upstream(self.up.url()) as clone:
            self.assertEqual(clone.resolve(self.c["c1"][:8]), self.c["c1"])
            self.assertIsNone(clone.resolve("0" * 40))

    def test_has_tells_whether_a_path_exists_at_a_commit(self):
        with adoption.Upstream(self.up.url()) as clone:
            self.assertTrue(clone.has(self.c["c1"], "skills/eng/r"))
            self.assertFalse(clone.has(self.c["c2"], "skills/eng/r"))
            self.assertTrue(clone.has(self.c["c2"], "."))

    def test_a_source_that_cannot_be_cloned_raises(self):
        with self.assertRaises(adoption.AdoptionError):
            adoption.Upstream("file:///nonexistent/repo")


class CopyIn(AdoptionCase):
    def test_a_folder_is_copied_with_its_files(self):
        self.adopt("skills/a", "skills/eng/a")
        self.assertIn("a v1", self.read("skills/a/SKILL.md"))
        self.assertTrue(os.path.exists(os.path.join(self.root, "skills/a/old.md")))

    def test_a_single_file_is_copied_and_its_sidecar_sits_beside_it(self):
        self.adopt("notes.md", "notes.md")
        self.assertEqual(self.read("notes.md"), "a single file\n")
        self.assertTrue(os.path.exists(os.path.join(self.root, "notes.md.provenance.json")))

    def test_copying_over_an_item_drops_files_upstream_deleted_but_keeps_the_sidecar(self):
        self.adopt("skills/a", "skills/eng/a")
        self.adopt("skills/a", "skills/eng/a", at="c2")
        self.assertFalse(os.path.exists(os.path.join(self.root, "skills/a/old.md")))
        self.assertEqual([e["commit"] for e in self.entries("skills/a")], [self.c["c1"], self.c["c2"]])

    def test_a_folder_without_a_sidecar_is_never_emptied(self):
        self.write("skills/a/mine.txt", "local work")
        with adoption.Upstream(self.up.url()) as clone:
            clone.checkout(self.c["c1"], ["skills/eng/a"])
            _kind, pruned = adoption.copy_in(clone, "skills/eng/a", os.path.join(self.root, "skills/a"))
        self.assertFalse(pruned)
        self.assertEqual(self.read("skills/a/mine.txt"), "local work")


class LocalDrift(AdoptionCase):
    def drift(self, local, path, at="c1"):
        with adoption.Upstream(self.up.url()) as clone:
            return adoption.local_drift(clone, self.c[at], path, os.path.join(self.root, local))

    def test_an_untouched_copy_has_no_drift(self):
        self.adopt("skills/a", "skills/eng/a")
        self.assertEqual(self.drift("skills/a", "skills/eng/a"), [])

    def test_each_kind_of_local_change_is_named(self):
        self.adopt("skills/a", "skills/eng/a")
        self.write("skills/a/SKILL.md", "edited")
        self.write("skills/a/extra.md", "new")
        os.remove(os.path.join(self.root, "skills/a/old.md"))
        self.assertEqual(self.drift("skills/a", "skills/eng/a"),
                         ["changed locally: SKILL.md", "added locally: extra.md", "deleted locally: old.md"])

    def test_files_git_ignores_are_not_part_of_the_copy(self):
        self.adopt("skills/a", "skills/eng/a")
        self.write("skills/a/.DS_Store", "junk")
        self.assertEqual(self.drift("skills/a", "skills/eng/a"), [])

    def test_a_single_file_item_is_compared_too(self):
        self.adopt("notes.md", "notes.md")
        self.assertEqual(self.drift("notes.md", "notes.md"), [])
        self.write("notes.md", "edited")
        self.assertEqual(self.drift("notes.md", "notes.md"), ["changed locally: notes.md"])

    def test_an_old_pin_missing_from_the_source_cannot_be_compared(self):
        self.adopt("skills/a", "skills/eng/a")
        with adoption.Upstream(self.up.url()) as clone:
            self.assertIsNone(adoption.local_drift(clone, "0" * 40, "skills/eng/a",
                                                   os.path.join(self.root, "skills/a")))


class RePin(AdoptionCase):
    def test_an_item_moves_to_upstream_head_and_its_content_follows(self):
        self.adopt("skills/a", "skills/eng/a")
        result = self.re_pin("skills/a")["skills/a"]
        self.assertEqual(result.status, "moved")
        self.assertIn("a v2", self.read("skills/a/SKILL.md"))
        self.assertEqual(self.entries("skills/a")[-1]["commit"], self.c["c3"])

    def test_the_new_entry_keeps_the_path_license_and_mode_of_the_old_pin(self):
        self.adopt("skills/a", "skills/eng/a")
        self.re_pin("skills/a", notes="why")
        old, new = self.entries("skills/a")
        for key in ("source", "path", "license", "adopted-as"):
            self.assertEqual(new[key], old[key])
        self.assertEqual(new["notes"], "why")

    def test_an_item_already_at_its_target_is_left_alone(self):
        self.adopt("skills/a", "skills/eng/a", at="c3")
        result = self.re_pin("skills/a")["skills/a"]
        self.assertEqual(result.status, "current")
        self.assertEqual(len(self.entries("skills/a")), 1)

    def test_an_explicit_commit_wins_over_the_comparison_target(self):
        self.adopt("skills/a", "skills/eng/a")
        self.re_pin("skills/a", commit=self.c["c2"][:10])
        self.assertEqual(self.entries("skills/a")[-1]["commit"], self.c["c2"])

    def test_an_item_that_tracks_releases_moves_to_the_release_not_to_head(self):
        self.adopt("skills/a", "skills/eng/a", track="release")
        self.re_pin("skills/a")
        self.assertEqual(self.entries("skills/a")[-1]["commit"], self.c["c2"])

    def test_an_inspired_by_item_only_gets_a_new_entry(self):
        self.adopt("plugins/p", "plugins/p1", mode="inspired-by")
        self.write("plugins/p/README.md", "my own words")
        result = self.re_pin("plugins/p")["plugins/p"]
        self.assertEqual(result.status, "moved")
        self.assertEqual(self.read("plugins/p/README.md"), "my own words")
        self.assertEqual(len(self.entries("plugins/p")), 2)

    def test_a_locally_edited_copy_is_not_overwritten(self):
        self.adopt("skills/a", "skills/eng/a")
        self.write("skills/a/SKILL.md", "my edit")
        result = self.re_pin("skills/a")["skills/a"]
        self.assertEqual(result.status, "failed")
        self.assertIn("changed locally: SKILL.md", result.detail)
        self.assertEqual(self.read("skills/a/SKILL.md"), "my edit")
        self.assertEqual(len(self.entries("skills/a")), 1)

    def test_overwrite_local_replaces_an_edited_copy(self):
        self.adopt("skills/a", "skills/eng/a")
        self.write("skills/a/SKILL.md", "my edit")
        result = self.re_pin("skills/a", overwrite_local=True)["skills/a"]
        self.assertEqual(result.status, "moved")
        self.assertIn("a v2", self.read("skills/a/SKILL.md"))

    def test_an_item_whose_path_vanished_upstream_fails_and_keeps_its_pin(self):
        self.adopt("skills/r", "skills/eng/r")
        result = self.re_pin("skills/r")["skills/r"]
        self.assertEqual(result.status, "failed")
        self.assertIn("no longer exists upstream", result.detail)
        self.assertEqual(len(self.entries("skills/r")), 1)
        self.assertTrue(os.path.exists(os.path.join(self.root, "skills/r/SKILL.md")))

    def test_a_path_without_a_sidecar_is_sent_to_adopt(self):
        result = self.re_pin("skills/nothing")["skills/nothing"]
        self.assertEqual(result.status, "failed")
        self.assertIn("bin/adopt", result.detail)

    def test_an_item_that_diverged_from_upstream_is_not_moved(self):
        self.adopt("skills/a", "skills/eng/a")
        sidecars.append(sidecars.sidecar_path(os.path.join(self.root, "skills/a")),
                        {"source": "self", "adopted-as": "inspired-by", "adopted-at": "2026-01-01"})
        result = self.re_pin("skills/a")["skills/a"]
        self.assertEqual(result.status, "failed")
        self.assertIn("diverged", result.detail)

    def test_one_failure_does_not_stop_the_other_items(self):
        self.adopt("skills/a", "skills/eng/a")
        self.adopt("skills/z", "skills/eng/z")
        self.write("skills/a/SKILL.md", "my edit")
        results = self.re_pin("skills/a", "skills/z")
        self.assertEqual((results["skills/a"].status, results["skills/z"].status), ("failed", "moved"))

    def test_a_source_is_cloned_once_and_its_structure_changes_are_said_once(self):
        self.adopt("skills/a", "skills/eng/a")
        self.adopt("skills/z", "skills/eng/z")
        clones = []
        original = adoption.Upstream.__init__

        def counting(clone, source):
            clones.append(source)
            original(clone, source)

        adoption.Upstream.__init__ = counting
        try:
            self.re_pin("skills/a", "skills/z")
        finally:
            adoption.Upstream.__init__ = original
        self.assertEqual(len(clones), 1)
        self.assertEqual(sum("NEW      skills/eng/c" in line for line in self.said), 1)

    def test_one_commit_cannot_be_given_for_items_from_two_sources(self):
        self.adopt("skills/a", "skills/eng/a")
        self.write("other/x.md", "x")
        sidecars.append(os.path.join(self.root, "other/x.md.provenance.json"),
                        sidecars.new_entry("https://example.invalid/other", "c" * 40, "x.md", "MIT",
                                           "inspired-by", "2026-01-01"))
        with self.assertRaises(adoption.AdoptionError):
            self.re_pin("skills/a", "other/x.md", commit=self.c["c2"])


if __name__ == "__main__":
    unittest.main()
