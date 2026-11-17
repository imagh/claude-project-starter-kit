"""Tests for guard.py: the PreToolUse hook that blocks whole reads of big files and foreground long-running commands."""
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guard  # noqa: E402

CONFIG = {
    "max_whole_read_bytes": 1000,
    "exempt_suffixes": [".png", ".pdf"],
    "background_only": [r"\bpytest\b", r"gradlew\b.*\b(check|test)\b"],
    "background_hint": "Use scripts/check.sh in the background.",
}


def read(path, **extra):
    return {"tool_name": "Read", "tool_input": dict({"file_path": str(path)}, **extra)}


def bash(command, background=None):
    tool_input = {"command": command}
    if background is not None:
        tool_input["run_in_background"] = background
    return {"tool_name": "Bash", "tool_input": tool_input}


class ReadRuleTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        self.big = self.root / "LOG.md"
        self.big.write_bytes(b"x" * 1001)
        self.at_limit = self.root / "small.md"
        self.at_limit.write_bytes(b"x" * 1000)

    def tearDown(self):
        self.dir.cleanup()

    def test_refuses_a_whole_read_of_a_big_file_and_says_what_to_do_instead(self):
        reason = guard.decide(read(self.big), CONFIG)
        self.assertIn("LOG.md", reason)
        self.assertIn("offset/limit", reason)
        self.assertIn("DIGEST.md", reason)

    def test_allows_a_file_at_the_limit(self):
        self.assertIsNone(guard.decide(read(self.at_limit), CONFIG))

    def test_allows_a_big_file_read_in_part(self):
        self.assertIsNone(guard.decide(read(self.big, offset=10, limit=5), CONFIG))
        self.assertIsNone(guard.decide(read(self.big, limit=5), CONFIG))
        self.assertIsNone(guard.decide(read(self.big, offset=10), CONFIG))

    def test_allows_exempt_suffixes_whatever_their_size(self):
        for name in ("diff_compare.png", "spec.PDF"):
            path = self.root / name
            path.write_bytes(b"x" * 5000)
            self.assertIsNone(guard.decide(read(path), CONFIG), name)

    def test_allows_a_path_that_does_not_exist(self):
        self.assertIsNone(guard.decide(read(self.root / "missing.md"), CONFIG))


class BashRuleTest(unittest.TestCase):
    def assert_refused(self, command):
        reason = guard.decide(bash(command), CONFIG)
        self.assertIsNotNone(reason, command)
        self.assertIn("background", reason)
        self.assertIn("scripts/check.sh", reason)

    def assert_allowed(self, command, background=None, config=CONFIG):
        self.assertIsNone(guard.decide(bash(command, background), config), command)

    def test_refuses_a_listed_command_in_the_foreground(self):
        self.assert_refused("pytest -q")
        self.assert_refused("cd /w && ./gradlew :app:check > log 2>&1")
        self.assert_refused("pytest tests/ | tee out.log")
        self.assert_refused("ruff check . ; pytest")

    def test_allows_a_backgrounded_run(self):
        self.assert_allowed("pytest -q > /tmp/x.log 2>&1 &")
        self.assert_allowed("pytest > /tmp/x.log 2>&1 & echo started")
        self.assert_allowed("pytest -q", background=True)

    def test_a_backgrounded_run_does_not_excuse_a_later_foreground_one(self):
        self.assert_refused("make build > a.log 2>&1 & pytest")

    def test_allows_commands_that_match_no_pattern(self):
        self.assert_allowed("./gradlew assembleRelease")
        self.assert_allowed("git log --oneline -3")

    def test_an_empty_pattern_list_blocks_nothing(self):
        self.assert_allowed("pytest -q", config=dict(CONFIG, background_only=[]))


class ConfigTest(unittest.TestCase):
    def test_loads_the_shipped_config_and_it_is_well_formed(self):
        config = guard.load_config()
        self.assertGreater(config["max_whole_read_bytes"], 0)
        self.assertIsInstance(config["background_only"], list)
        self.assertIn(".png", config["exempt_suffixes"])

    def test_a_missing_or_broken_config_falls_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            broken = Path(d) / "guard.json"
            broken.write_text("{not json")
            self.assertEqual(guard.DEFAULTS, guard.load_config(broken))
            self.assertEqual(guard.DEFAULTS, guard.load_config(Path(d) / "absent.json"))


class OtherInputTest(unittest.TestCase):
    def test_other_tools_and_malformed_input_are_allowed(self):
        self.assertIsNone(guard.decide({"tool_name": "Edit", "tool_input": {"file_path": "x"}}, CONFIG))
        self.assertIsNone(guard.decide({}, CONFIG))
        self.assertIsNone(guard.decide({"tool_name": "Bash", "tool_input": "not a dict"}, CONFIG))
        self.assertIsNone(guard.decide({"tool_name": "Read", "tool_input": {"file_path": 7}}, CONFIG))


class MainTest(unittest.TestCase):
    def run_main(self, stdin_text):
        err = io.StringIO()
        code = guard.main(io.StringIO(stdin_text), err, CONFIG)
        return code, err.getvalue()

    def test_blocks_with_exit_code_2_and_the_reason_on_stderr(self):
        code, err = self.run_main(json.dumps(bash("pytest")))
        self.assertEqual(2, code)
        self.assertIn("scripts/check.sh", err)

    def test_allows_with_exit_code_0_and_no_output(self):
        self.assertEqual((0, ""), self.run_main(json.dumps(bash("ls"))))

    def test_unreadable_input_fails_open(self):
        self.assertEqual((0, ""), self.run_main("not json"))


if __name__ == "__main__":
    unittest.main()
