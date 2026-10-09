"""The fake upstream repositories the tests run against.

Both test layers use this: tests/test_*.py import it, and tests/run.sh runs it
as a script to build the same repository for the end-to-end checks. Every git
call ignores the user's global and system config.
"""
import os
import shutil
import subprocess
import sys


class Repo:
    """A throwaway git repository built commit by commit."""

    def __init__(self, path):
        self.path = path
        os.makedirs(path, exist_ok=True)
        self._home = path + ".home"
        os.makedirs(self._home, exist_ok=True)
        self.git("init", "-q", "-b", "main")

    def git(self, *args):
        env = dict(os.environ, HOME=self._home, GIT_CONFIG_NOSYSTEM="1")
        return subprocess.run(
            ["git", "-C", self.path, "-c", "user.name=test", "-c", "user.email=test@example.invalid", *args],
            capture_output=True, text=True, env=env)

    def put(self, rel, text):
        full = os.path.join(self.path, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text + "\n")

    def skill(self, rel, body="body"):
        name = os.path.basename(rel)
        self.put(f"{rel}/SKILL.md", f"---\nname: {name}\ndescription: fixture skill\n---\n{body}")

    def plugin(self, rel):
        self.put(f"{rel}/.claude-plugin/plugin.json", "{}")

    def remove(self, rel):
        full = os.path.join(self.path, rel)
        if os.path.isdir(full):
            shutil.rmtree(full)
        else:
            os.remove(full)

    def commit(self, message, tag=None):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        if tag:
            self.git("tag", tag)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def url(self):
        return "file://" + self.path


def build(path):
    """Build the standard upstream at path. Returns its Repo and commits c1, c2, c3.

    c1 is the state items are first adopted from. c2 changes content, removes
    an entry, and adds entries in every position the structure scan cares
    about. c3 changes nothing structural.
    """
    repo = Repo(path)

    repo.skill("skills/eng/a", "a v1")
    repo.put("skills/eng/a/old.md", "dropped in c2")
    repo.skill("skills/eng/b")
    repo.skill("skills/eng/r")
    repo.skill("skills/eng/z")
    repo.skill("skills/beta/old")
    repo.skill("skills/prod/p")
    repo.plugin("plugins/p1")
    repo.skill("plugins/p1/skills/s1")
    repo.put("notes.md", "a single file")
    c1 = repo.commit("c1")

    repo.skill("skills/eng/a", "a v2")
    repo.remove("skills/eng/a/old.md")
    repo.remove("skills/eng/r")
    repo.skill("skills/eng/c")            # new sibling of a tracked path
    repo.skill("skills/eng/a/sub")        # inside a tracked path
    repo.skill("skills/eng/b/deep")       # nested in an existing, unadopted skill
    repo.skill("skills/beta/new")         # new skill outside the tracked dirs
    repo.skill("skills/prod/q")           # new sibling of a tracked path pinned elsewhere
    repo.skill("plugins/p1/skills/s2")    # new skill inside an existing plugin
    repo.plugin("plugins/p2")
    repo.skill("plugins/p2/skills/x")     # new plugin, with a skill nested in it
    repo.skill("docs/ünï")                # non-ASCII path
    repo.put("notes.md", "a single file, edited")
    c2 = repo.commit("c2")

    c3 = repo.commit("c3")
    return repo, {"c1": c1, "c2": c2, "c3": c3}


if __name__ == "__main__":
    # tests/run.sh: eval "$(python3 tests/upstream.py <dir>)"
    _repo, commits = build(sys.argv[1])
    for name, sha in commits.items():
        print(f"{name.upper()}={sha}")
