"""Tests for lib/declarations.py: what is declared, and the hints that say how to create it."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import declarations


class RepoCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def declare(self, kind, name, readme="readme"):
        d = os.path.join(self.root, "user", "shared", kind, name)
        os.makedirs(d, exist_ok=True)
        if readme is not None:
            with open(os.path.join(d, "README.md"), "w") as f:
                f.write(readme)

    def settings(self, data, template=None):
        d = (os.path.join(self.root, "project-templates", template, ".claude") if template
             else os.path.join(self.root, "user", "shared"))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "settings.json"), "w") as f:
            json.dump(data, f)


class Declared(RepoCase):
    def test_every_directory_is_a_declaration(self):
        self.declare("plugins", "b")
        self.declare("plugins", "a")
        self.assertEqual(declarations.declared(self.root, "plugins"), ["a", "b"])

    def test_an_mcp_server_without_a_readme_is_still_declared(self):
        self.declare("mcp", "srv", readme=None)
        self.assertEqual(declarations.declared(self.root, "mcp"), ["srv"])

    def test_nothing_declared_when_the_directory_is_absent(self):
        self.assertEqual(declarations.declared(self.root, "mcp"), [])


class PluginEntries(RepoCase):
    def test_user_scope_wins_over_a_template(self):
        self.settings({"enabledPlugins": {"p@user-market": True}})
        self.settings({"enabledPlugins": {"p@template-market": True}}, template="t")
        self.assertEqual(declarations.plugin_entries(self.root)["p"], ("user-market", "user"))

    def test_a_false_entry_enables_nothing_but_keeps_the_marketplace(self):
        self.settings({"enabledPlugins": {"p@market": False}})
        self.assertEqual(declarations.plugin_entries(self.root)["p"], ("market", ""))

    def test_a_template_that_enables_wins_over_a_user_entry_that_is_off(self):
        self.settings({"enabledPlugins": {"p@market": False}})
        self.settings({"enabledPlugins": {"p@market": True}}, template="t")
        self.assertEqual(declarations.plugin_entries(self.root)["p"], ("market", "project"))

    def test_missing_or_broken_settings_enable_nothing(self):
        os.makedirs(os.path.join(self.root, "user", "shared"))
        with open(os.path.join(self.root, "user", "shared", "settings.json"), "w") as f:
            f.write("{not json")
        self.assertEqual(declarations.plugin_entries(self.root), {})


class Hints(RepoCase):
    def setUp(self):
        super().setUp()
        for name in ("builtin", "third", "proj", "orphan"):
            self.declare("plugins", name)
        self.declare("mcp", "srv")
        self.settings({
            "enabledPlugins": {"builtin@official": True, "third@other": True},
            "extraKnownMarketplaces": {"other": {"source": {"source": "github", "repo": "owner/repo"}}},
        })
        self.settings({"enabledPlugins": {"proj@official": True}}, template="t")

    def test_rows_group_built_in_then_third_party_then_unknown(self):
        self.assertEqual(declarations.plugin_rows(self.root), [
            ("builtin", "official", "", "user"),
            ("proj", "official", "", "project"),
            ("third", "other", "owner/repo", "user"),
            ("orphan", "", "", ""),
        ])

    def test_install_hints_give_one_marketplace_line_per_group(self):
        self.assertEqual(declarations.install_hints(self.root), [
            "",
            "Declared plugins (NOT installed by this script — see user/shared/plugins/):",
            "",
            "Inside a Claude Code session, run:",
            "",
            "  # official (built-in marketplace — no 'marketplace add' needed)",
            "  /plugin install builtin@official",
            "  /plugin install proj@official   # project-scope only (see user/shared/plugins/proj/README.md)",
            "",
            "  # other (third-party marketplace — add it before installing)",
            "  /plugin marketplace add owner/repo",
            "  /plugin install third@other",
            "",
            "  # No settings.json enables these — add them to enabledPlugins, or install by hand:",
            "  #   - orphan",
            "",
            "Declared MCP servers (NOT registered by this script — see user/shared/mcp/):",
            "  - srv",
            "",
            "For each, open user/shared/mcp/<name>/README.md and run the registration",
            "command shown there (typically: claude mcp add --scope user ...).",
        ])

    def test_uninstall_hints_name_each_plugin_and_server(self):
        hints = declarations.uninstall_hints(self.root)
        self.assertIn("  /plugin uninstall third@other", hints)
        self.assertIn("  # orphan — marketplace unknown; check user/shared/plugins/orphan/README.md", hints)
        self.assertIn("  - srv", hints)

    def test_no_declarations_means_no_hints(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(declarations.install_hints(empty), [])
            self.assertEqual(declarations.uninstall_hints(empty), [])


if __name__ == "__main__":
    unittest.main()
