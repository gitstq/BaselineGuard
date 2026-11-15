"""End-to-end CLI tests (no installation required)."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from baselineguard.cli import main

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
RULES_JSON = ROOT / "src" / "baselineguard" / "data" / "rules.json"


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        code = main(argv)
    return code, buf.getvalue()


class ScanCliTests(unittest.TestCase):
    def test_json_report_contains_error(self):
        code, out = run(["scan", str(FIXTURES), "--format", "json"])
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertGreaterEqual(report["counts"]["error"], 2)
        self.assertEqual(report["exit_code"], 1)
        self.assertFalse(report["passed"])
        ids = {f["rule_id"] for f in report["findings"]}
        self.assertIn("html-marquee", ids)
        self.assertIn("html-center", ids)

    def test_commented_features_absent_from_report(self):
        _, out = run(["scan", str(FIXTURES), "--format", "json"])
        ids = {f["rule_id"] for f in json.loads(out)["findings"]}
        self.assertNotIn("html-font", ids)
        self.assertNotIn("js-document-write", ids)

    def test_fail_on_none_always_passes(self):
        code, _ = run(["scan", str(FIXTURES), "--fail-on", "none"])
        self.assertEqual(code, 0)

    def test_fail_on_warning(self):
        code, _ = run(["scan", str(FIXTURES / "sample.css"), "--fail-on", "warning"])
        self.assertEqual(code, 1)

    def test_allow_newly_and_allow_limited_reduce_errors(self):
        _, plain = run(["scan", str(FIXTURES), "--format", "json"])
        _, relaxed = run(["scan", str(FIXTURES), "--format", "json",
                          "--allow-newly", "--allow-limited"])
        self.assertLess(json.loads(relaxed)["counts"]["error"], json.loads(plain)["counts"]["error"])

    def test_markdown_report(self):
        code, out = run(["scan", str(FIXTURES), "--format", "markdown", "--fail-on", "none"])
        self.assertEqual(code, 0)
        self.assertIn("## BaselineGuard report", out)
        self.assertIn("| Severity | Rule |", out)

    def test_output_file_and_quiet(self):
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "sub" / "report.json"
            code, out = run(["scan", str(FIXTURES), "--format", "json",
                             "--fail-on", "none", "-o", str(dest), "--quiet"])
            self.assertEqual(code, 0)
            self.assertEqual(out, "")
            self.assertTrue(dest.is_file())
            self.assertEqual(json.loads(dest.read_text(encoding="utf-8"))["tool"], "BaselineGuard")

    def test_missing_path_returns_usage_error(self):
        code, _ = run(["scan", "/definitely/not/here"])
        self.assertEqual(code, 2)

    def test_invalid_baseline_returns_usage_error(self):
        code, _ = run(["scan", str(FIXTURES), "--baseline", "not-a-year"])
        self.assertEqual(code, 2)

    def test_baseline_year_changes_counts(self):
        _, narrow = run(["scan", str(FIXTURES), "--format", "json", "--baseline", "2016", "--fail-on", "none"])
        _, wide = run(["scan", str(FIXTURES), "--format", "json", "--baseline", "2024", "--fail-on", "none"])
        self.assertGreater(json.loads(narrow)["counts"]["warning"],
                           json.loads(wide)["counts"]["warning"])


class ContextCliTests(unittest.TestCase):
    def test_stdout_mode(self):
        code, out = run(["context", "--stdout", "--format", "claude-md"])
        self.assertEqual(code, 0)
        self.assertIn("<!-- baselineguard:begin -->", out)
        self.assertIn("Claude", out)

    def test_writes_default_file(self):
        with tempfile.TemporaryDirectory() as d:
            out_path = Path(d) / "AGENTS.md"
            code, out = run(["context", "--out", str(out_path)])
            self.assertEqual(code, 0)
            self.assertIn("context created", out)
            self.assertIn("baselineguard:begin", out_path.read_text(encoding="utf-8"))


class RulesCliTests(unittest.TestCase):
    def test_validate_bundled(self):
        code, out = run(["rules", "validate", str(RULES_JSON)])
        self.assertEqual(code, 0)
        self.assertIn("VALID", out)

    def test_validate_invalid_file(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "bad.json"
            bad.write_text('{"rules": [{"id": "oops"}]}', encoding="utf-8")
            code, out = run(["rules", "validate", str(bad)])
            self.assertEqual(code, 1)
            self.assertIn("INVALID", out)

    def test_list_json(self):
        code, out = run(["rules", "list", "--format", "json"])
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)), 41)

    def test_show_rule(self):
        code, out = run(["rules", "show", "css-has"])
        self.assertEqual(code, 0)
        self.assertIn('"status": "newly"', out)

    def test_show_unknown_rule(self):
        code, _ = run(["rules", "show", "does-not-exist"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
