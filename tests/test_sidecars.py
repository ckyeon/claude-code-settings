"""Tests for lib/sidecars.py, crossed at the interface its callers use."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import sidecars


def entry(source, commit="c1", path="skills/a", **extra):
    e = {"source": source, "commit": commit, "path": path, "license": "MIT",
         "adopted-as": "copied", "adopted-at": "2026-01-01"}
    e.update(extra)
    return e


SELF = {"source": "self", "adopted-as": "inspired-by", "adopted-at": "2026-01-02"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class RepoCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def write(self, rel, data):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))
        return path


class CurrentPins(unittest.TestCase):
    def test_newest_entry_of_a_source_is_its_pin(self):
        pins = sidecars.current_pins([entry("https://x/r", "old"), entry("https://x/r", "new")])
        self.assertEqual([p["commit"] for p in pins], ["new"])

    def test_two_spellings_of_one_repo_are_one_source(self):
        pins = sidecars.current_pins([entry("https://x/r.git", "old"), entry("https://x/r/", "new")])
        self.assertEqual([p["commit"] for p in pins], ["new"])

    def test_each_source_keeps_its_own_pin(self):
        pins = sidecars.current_pins([entry("https://x/a", "a1"), entry("https://x/b", "b1"),
                                      entry("https://x/a", "a2")])
        self.assertEqual(sorted(p["commit"] for p in pins), ["a2", "b1"])

    def test_item_whose_newest_entry_is_self_has_no_pins(self):
        self.assertEqual(sidecars.current_pins([entry("https://x/r"), SELF]), [])

    def test_item_re_adopted_after_self_is_tracked_again(self):
        pins = sidecars.current_pins([entry("https://x/r", "old"), SELF, entry("https://x/r", "new")])
        self.assertEqual([p["commit"] for p in pins], ["new"])


class Read(RepoCase):
    def test_folder_sidecar_describes_its_folder(self):
        self.write("skills/a/.provenance.json", {"provenance": [entry("https://x/r")]})
        items, unreadable = sidecars.read(self.root)
        self.assertEqual([(i.local, i.sidecar) for i in items],
                         [("skills/a", "skills/a/.provenance.json")])
        self.assertEqual(unreadable, [])

    def test_file_sidecar_describes_the_file_beside_it(self):
        self.write("CLAUDE.md.provenance.json", {"provenance": [entry("https://x/r")]})
        items, _ = sidecars.read(self.root)
        self.assertEqual(items[0].local, "CLAUDE.md")

    def test_track_is_read_from_the_top_level(self):
        self.write("a/.provenance.json", {"track": "release", "provenance": [entry("https://x/r")]})
        self.write("b/.provenance.json", {"provenance": [entry("https://x/r")]})
        items, _ = sidecars.read(self.root)
        self.assertEqual([i.track for i in items], ["release", ""])

    def test_unreadable_sidecars_are_reported_not_dropped_silently(self):
        self.write("ok/.provenance.json", {"provenance": [entry("https://x/r")]})
        self.write("bad/.provenance.json", "{not json")
        self.write("odd/.provenance.json", {"provenance": "nope"})
        items, unreadable = sidecars.read(self.root)
        self.assertEqual([i.local for i in items], ["ok"])
        self.assertEqual([rel for rel, _ in unreadable],
                         ["bad/.provenance.json", "odd/.provenance.json"])

    def test_git_and_node_modules_are_not_walked(self):
        self.write(".git/x/.provenance.json", {"provenance": [entry("https://x/r")]})
        self.write("node_modules/y/.provenance.json", {"provenance": [entry("https://x/r")]})
        self.assertEqual(sidecars.read(self.root), ([], []))


class TrackedPaths(RepoCase):
    def test_only_current_pins_of_the_source_count(self):
        self.write("a/.provenance.json", {"provenance": [
            entry("https://x/r", "old", "skills/old-name"), entry("https://x/r.git", "new", "skills/a")]})
        self.write("b/.provenance.json", {"provenance": [entry("https://x/other", path="skills/b")]})
        self.write("whole/.provenance.json", {"provenance": [entry("https://x/r", path=".")]})
        self.write("gone/.provenance.json", {"provenance": [entry("https://x/r", path="skills/gone"), SELF]})
        items, _ = sidecars.read(self.root)
        self.assertEqual(sidecars.tracked_paths(items, "https://x/r"), {"skills/a"})


class PinFor(unittest.TestCase):
    def test_pin_for_matches_across_spellings(self):
        item = sidecars.Item("a", "a/.provenance.json",
                             [entry("https://x/r.git", "c9"), entry("https://x/b", "b1")], "")
        self.assertEqual(item.pin_for("https://x/r")["commit"], "c9")
        self.assertIsNone(item.pin_for("https://x/unknown"))


class Append(RepoCase):
    def test_append_creates_the_sidecar(self):
        path = os.path.join(self.root, "a.provenance.json")
        sidecars.append(path, sidecars.new_entry("https://x/r", "c1", "p", "MIT", "copied", "2026-01-01"))
        data = load(path)
        self.assertEqual(list(data["provenance"][0]),
                         ["source", "commit", "path", "license", "adopted-as", "adopted-at"])

    def test_append_keeps_history_and_top_level_keys(self):
        path = self.write("a/.provenance.json", {"track": "release", "provenance": [entry("https://x/r")]})
        sidecars.append(path, sidecars.new_entry("https://x/r", "c2", "p", "MIT", "copied",
                                                 "2026-01-02", notes="why"))
        data = load(path)
        self.assertEqual(data["track"], "release")
        self.assertEqual([e["commit"] for e in data["provenance"]], ["c1", "c2"])
        self.assertEqual(data["provenance"][1]["notes"], "why")

    def test_append_refuses_a_file_that_is_not_a_sidecar(self):
        path = self.write("a/.provenance.json", {"other": 1})
        with self.assertRaises(ValueError):
            sidecars.append(path, entry("https://x/r"))
        self.assertEqual(load(path), {"other": 1})


class SidecarPath(RepoCase):
    def test_folder_item_keeps_its_sidecar_inside(self):
        os.makedirs(os.path.join(self.root, "skills/a"))
        self.assertEqual(sidecars.sidecar_path(os.path.join(self.root, "skills/a")),
                         os.path.join(self.root, "skills/a/.provenance.json"))

    def test_file_item_keeps_its_sidecar_beside_it(self):
        path = self.write("CLAUDE.md", "text")
        self.assertEqual(sidecars.sidecar_path(path), path + ".provenance.json")


class Validate(RepoCase):
    def problems(self):
        return [msg for _rel, msg in sidecars.validate(self.root)]

    def test_complete_sidecar_has_no_problems(self):
        self.write("a/.provenance.json", {"track": "release", "provenance": [entry("https://x/r"), SELF]})
        self.assertEqual(self.problems(), [])

    def test_each_breach_is_named(self):
        self.write("a/.provenance.json", "{not json")
        self.write("b/.provenance.json", {"provenance": []})
        self.write("c/.provenance.json", {"trak": "release", "provenance": [entry("https://x/r")]})
        self.write("d/.provenance.json", {"track": "nightly", "provenance": [entry("https://x/r")]})
        self.write("e/.provenance.json", {"provenance": [{"source": "https://x/r", "adopted-as": "copied"}]})
        problems = self.problems()
        self.assertTrue(problems[0].startswith("invalid JSON"))
        self.assertEqual(problems[1:], [
            "provenance[] missing or empty",
            "unknown top-level key(s): trak",
            "track 'nightly' is not one of: release, marketplace",
            "provenance[0] missing: commit, path, license",
        ])

    def test_self_entry_needs_no_commit_path_or_license(self):
        self.write("a/.provenance.json", {"provenance": [SELF]})
        self.assertEqual(self.problems(), [])


if __name__ == "__main__":
    unittest.main()
