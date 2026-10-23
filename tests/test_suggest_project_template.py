"""Tests for user/shared/hooks/suggest-project-template.py: when a session start counts as a new project."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "..", "user", "shared", "hooks", "suggest-project-template.py")
spec = importlib.util.spec_from_file_location("suggest_project_template", HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

GIT_ENV = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


class Suggestion(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = os.path.join(self._tmp.name, "home")
        self.dir = os.path.join(self._tmp.name, "project")
        os.makedirs(self.home)
        os.makedirs(self.dir)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text=""):
        path = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def commit(self, n):
        git = ["git", "-C", self.dir, "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
        subprocess.run(git + ["init", "-q"], check=True, env=GIT_ENV)
        for i in range(n):
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", str(i)], check=True, env=GIT_ENV)

    def suggest(self, source="startup", cwd=None, roots=(), now=None):
        payload = {"source": source, "cwd": cwd or self.dir}
        return hook.suggestion(payload, self.home, list(roots), now or time.time())

    def test_an_empty_directory_is_a_new_project(self):
        self.assertEqual(self.suggest(), hook.NOTE)

    def test_only_a_fresh_session_counts(self):
        self.assertIsNone(self.suggest(source="resume"))

    def test_the_home_directory_never_counts(self):
        self.assertIsNone(self.suggest(cwd=self.home))

    def test_a_directory_under_a_temp_root_never_counts(self):
        self.assertIsNone(self.suggest(roots=[self._tmp.name]))

    def test_a_claude_md_means_the_project_is_set_up(self):
        self.write("CLAUDE.md")
        self.assertIsNone(self.suggest())

    def test_project_settings_mean_the_project_is_set_up(self):
        self.write(".claude/settings.json", "{}")
        self.assertIsNone(self.suggest())

    def test_a_claude_dir_without_settings_still_counts(self):
        self.write(".claude/skills/x/SKILL.md")
        self.assertEqual(self.suggest(), hook.NOTE)

    def test_one_commit_still_counts_but_two_do_not(self):
        self.commit(1)
        self.assertEqual(self.suggest(), hook.NOTE)
        self.commit(1)
        self.assertIsNone(self.suggest())

    def test_a_file_older_than_a_day_means_an_existing_project(self):
        self.write("main.py")
        self.assertIsNone(self.suggest(now=time.time() + 2 * hook.DAY))

    def test_dependency_directories_are_not_aged(self):
        self.write("node_modules/pkg/index.js")
        self.assertEqual(self.suggest(now=time.time() + 2 * hook.DAY), hook.NOTE)

    def test_too_many_files_never_count(self):
        limit = hook.MAX_FILES
        hook.MAX_FILES = 2
        try:
            for name in ("a", "b", "c"):
                self.write(name)
            self.assertIsNone(self.suggest())
        finally:
            hook.MAX_FILES = limit


class Main(unittest.TestCase):
    def run_hook(self, stdin, env):
        return subprocess.run([sys.executable, HOOK], input=stdin, capture_output=True, text=True, env=env)

    def test_unreadable_input_prints_nothing(self):
        proc = self.run_hook("not json", dict(os.environ))
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    @unittest.skipIf(os.path.realpath(tempfile.gettempdir()).startswith(os.path.realpath("/tmp")),
                     "the test directory is under /tmp, which the hook always skips")
    def test_a_new_project_gets_the_note_as_additional_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "project"))
            env = dict(os.environ, HOME=os.path.join(tmp, "home"), TMPDIR=os.path.join(tmp, "tmp"))
            proc = self.run_hook(json.dumps({"source": "startup", "cwd": os.path.join(tmp, "project")}), env)
        out = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual((out["hookEventName"], out["additionalContext"]), ("SessionStart", hook.NOTE))


if __name__ == "__main__":
    unittest.main()
