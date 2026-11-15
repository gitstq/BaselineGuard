"""Tests for AI coding-agent context generation and idempotent insertion."""

import tempfile
import unittest
from pathlib import Path

from baselineguard.context import (
    DEFAULT_OUTPUTS, FORMATS, build_context, markers, write_context,
)
from baselineguard.rules import load_default_ruleset
from baselineguard.verdict import Policy


class ContextContentTests(unittest.TestCase):
    def setUp(self):
        self.rs = load_default_ruleset()
        self.p = Policy(2021, "widely")

    def test_all_formats_contain_markers(self):
        for fmt in FORMATS:
            with self.subTest(fmt=fmt):
                begin, end = markers(fmt)
                text = build_context(self.rs, self.p, fmt)
                self.assertIn(begin, text)
                self.assertIn(end, text)
                self.assertIn("Instructions", text)
                self.assertIn("ALLOW", text)
                self.assertIn("REVIEW", text)
                self.assertIn("DENY", text)

    def test_deny_list_contains_deprecated_rules(self):
        text = build_context(self.rs, self.p, "agents-md")
        deny_section = text.split("DENY - forbidden")[1].split("Regenerate:")[0]
        self.assertIn("html-marquee", deny_section)
        self.assertIn("js-document-write", deny_section)

    def test_limited_is_denied_by_default_but_reviewed_when_allowed(self):
        default = build_context(self.rs, self.p, "agents-md")
        self.assertIn("css-view-transitions", default.split("DENY - forbidden")[1])
        relaxed = build_context(self.rs, Policy(2021, "widely", allow_limited=True), "agents-md")
        review_block = relaxed.split("### REVIEW - requires explicit approval")[1].split("### DENY")[0]
        self.assertIn("css-view-transitions", review_block)

    def test_baseline_year_changes_allow_list(self):
        narrow = build_context(self.rs, Policy(2018, "2018"), "markdown")
        wide = build_context(self.rs, Policy(2024, "2024"), "markdown")
        a = narrow.split("ALLOW - safe to use")[1].split("REVIEW")[0]
        b = wide.split("ALLOW - safe to use")[1].split("REVIEW")[0]
        self.assertGreater(len(b), len(a))

    def test_unknown_format_raises(self):
        with self.assertRaises(ValueError):
            build_context(self.rs, self.p, "nope")

    def test_default_outputs_cover_all_formats(self):
        self.assertEqual(set(DEFAULT_OUTPUTS), set(FORMATS))


class WriteContextTests(unittest.TestCase):
    def setUp(self):
        self.rs = load_default_ruleset()
        self.p = Policy(2021, "widely")

    def test_created_then_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "AGENTS.md"
            content = build_context(self.rs, self.p, "agents-md")
            self.assertEqual(write_context(out, content, "agents-md"), "created")
            first = out.read_text(encoding="utf-8")
            self.assertEqual(write_context(out, content, "agents-md"), "unchanged")
            self.assertEqual(out.read_text(encoding="utf-8"), first)

    def test_preserves_surrounding_human_content(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "AGENTS.md"
            out.write_text("# My project\n\nHand-written rules live here.\n", encoding="utf-8")
            write_context(out, build_context(self.rs, self.p, "agents-md"), "agents-md")
            self.assertIn("Hand-written rules live here.", out.read_text(encoding="utf-8"))
            # second run with a different policy must replace only the block
            write_context(out, build_context(self.rs, Policy(2024, "2024"), "agents-md"), "agents-md")
            text = out.read_text(encoding="utf-8")
            self.assertIn("Hand-written rules live here.", text)
            self.assertEqual(text.count(markers("agents-md")[0]), 1)
            self.assertIn("2024", text)

    def test_cursorrules_uses_hash_markers(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / ".cursorrules"
            write_context(out, build_context(self.rs, self.p, "cursorrules"), "cursorrules")
            text = out.read_text(encoding="utf-8")
            self.assertIn("# baselineguard:begin", text)
            self.assertNotIn("<!--", text)
            self.assertNotIn("| --- |", text)


if __name__ == "__main__":
    unittest.main()
