"""Tests for user/shared/hooks/flag-prose-symbols.py: which symbols in Markdown prose it reports after Write and Edit."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "..", "user", "shared", "hooks", "flag-prose-symbols.py")


class FlagProseSymbols(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def run_hook(self, tool_name, tool_input, text):
        """text를 파일에 써 둔 다음 hook을 돌리고, 알린 내용을 돌려준다. 알리지 않았으면 None이다."""
        with open(tool_input["file_path"], "w", encoding="utf-8") as f:
            f.write(text)
        payload = {"hook_event_name": "PostToolUse", "tool_name": tool_name,
                   "tool_input": tool_input, "tool_response": {}}
        out = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                             capture_output=True, text=True, check=True).stdout
        if not out.strip():
            return None
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]

    def write(self, text, name="doc.md"):
        path = os.path.join(self.dir, name)
        return self.run_hook("Write", {"file_path": path, "content": text}, text)

    def edit(self, text, new_string):
        path = os.path.join(self.dir, "doc.md")
        return self.run_hook("Edit", {"file_path": path, "old_string": "x", "new_string": new_string,
                                      "replace_all": False}, text)

    def test_write_reports_semicolon_and_arrow_lines(self):
        context = self.write("# 제목\n\n앞 절이다; 뒤 절이다.\n\nA → B로 바꾼다.\n")
        self.assertIn("3행 [;]", context)
        self.assertIn("5행 [→]", context)

    def test_write_skips_places_the_rule_allows(self):
        text = ("---\ndescription: a; b\n---\n\n```\nx -> y;\n```\n\n| a; b |\n> 인용; 원문\n\n"
                "`a;b`와 \"x; y\"와 [링크](http://e.com/a;b)는 그대로다.\n")
        self.assertIsNone(self.write(text))

    def test_edit_reports_only_what_new_string_wrote(self):
        self.assertIsNone(self.edit("옛 절이다; 새 단어다.\n", "새 단어다."))
        context = self.edit("옛 줄이다; 그대로 둔다.\n\n새 줄이다; 고친다.\n", "새 줄이다; 고친다.")
        self.assertIn("3행 [;]", context)
        self.assertNotIn("1행", context)

    def test_edit_inside_existing_fence_is_code(self):
        self.assertIsNone(self.edit("설명이다.\n\n```python\nx = 1; y = 2\n```\n", "x = 1; y = 2"))

    def test_ignores_files_that_are_not_markdown(self):
        self.assertIsNone(self.write("a; b\n", name="note.txt"))


if __name__ == "__main__":
    unittest.main()
