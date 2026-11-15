"""Tests for file discovery, comment masking and feature detection."""

import tempfile
import unittest
from pathlib import Path

from baselineguard.detector import detect, iter_files, strip_comments
from baselineguard.rules import load_default_ruleset

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class CommentMaskingTests(unittest.TestCase):
    def test_length_and_newlines_preserved(self):
        src = "a();\n/* hello\nworld */\nb();\n"
        masked = strip_comments(src, True)
        self.assertEqual(len(masked), len(src))
        self.assertEqual(masked.count("\n"), src.count("\n"))

    def test_block_comment_content_is_masked(self):
        src = "/* document.write('x') */\ndocument.write('y');\n"
        masked = strip_comments(src, True)
        self.assertNotIn("document.write('x')", masked)
        self.assertIn("document.write('y')", masked)

    def test_html_comment_is_masked(self):
        src = "<!-- <marquee>x</marquee> -->\n<marquee>y</marquee>\n"
        masked = strip_comments(src, False)
        self.assertNotIn("<marquee>x", masked)
        self.assertIn("<marquee>y", masked)

    def test_url_survives_line_comment_masking(self):
        src = (
            'const u = "https://example.com/a";\n'
            'const s = "document.write in a string";\n'
            '// legacy document.write("z")\n'
        )
        masked = strip_comments(src, True)
        self.assertIn("https://example.com/a", masked)
        self.assertIn('"document.write in a string"', masked)
        self.assertNotIn('legacy document.write', masked)


class IterFilesTests(unittest.TestCase):
    def test_default_ignores(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "node_modules").mkdir()
            (root / "src" / "a.css").write_text("a{}", encoding="utf-8")
            (root / "node_modules" / "b.css").write_text("b{}", encoding="utf-8")
            rels = [rel for _, _, rel in iter_files(root)]
        self.assertEqual(rels, ["src/a.css"])

    def test_exclude_glob(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.css").write_text("a{}", encoding="utf-8")
            (root / "b.css").write_text("b{}", encoding="utf-8")
            rels = [rel for _, _, rel in iter_files(root, excludes=["b.css"])]
        self.assertEqual(rels, ["a.css"])

    def test_docs_skipped_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "README.md").write_text("display: grid", encoding="utf-8")
            (root / "a.css").write_text("a{}", encoding="utf-8")
            self.assertEqual([rel for _, _, rel in iter_files(root)], ["a.css"])
            self.assertEqual(len(list(iter_files(root, include_docs=True))), 2)


class DetectionTests(unittest.TestCase):
    def setUp(self):
        self.rs = load_default_ruleset()

    def _hits(self, rel):
        files = list(iter_files(FIXTURES / rel))
        hits, _, _ = detect(files, self.rs)
        return hits

    def test_deprecated_features_detected(self):
        ids = {h.rule_id for h in self._hits("sample.html")}
        self.assertIn("html-marquee", ids)
        self.assertIn("html-center", ids)
        self.assertIn("css-grid", ids)

    def test_commented_out_feature_not_detected(self):
        ids = {h.rule_id for h in self._hits("sample.html")}
        self.assertNotIn("html-font", ids, "feature inside an HTML comment must be ignored")
        self.assertNotIn("js-document-write", ids, "feature inside a JS block comment must be ignored")

    def test_newly_and_limited_detected(self):
        ids = {h.rule_id for h in self._hits("sample.css")}
        self.assertIn("css-has", ids)
        self.assertIn("css-view-transitions", ids)

    def test_js_rules_and_comment_masking(self):
        ids = {h.rule_id for h in self._hits("sample.js")}
        self.assertIn("js-fetch", ids)
        self.assertIn("js-structured-clone", ids)
        self.assertNotIn("js-document-write", ids)

    def test_same_rule_same_line_deduplicated(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "x.css").write_text(
                "a { display: grid; grid-template-columns: 1fr 1fr; grid-area: a; }\n",
                encoding="utf-8",
            )
            files = list(iter_files(root))
            hits, nfiles, nlines = detect(files, self.rs)
        self.assertEqual(nfiles, 1)
        self.assertEqual(nlines, 1)
        grid_hits = [h for h in hits if h.rule_id == "css-grid"]
        self.assertEqual(len(grid_hits), 1)

    def test_line_numbers_are_correct(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "x.html").write_text("<p>a</p>\n<marquee>b</marquee>\n", encoding="utf-8")
            hits, _, _ = detect(list(iter_files(root)), self.rs)
        self.assertEqual([h.line for h in hits if h.rule_id == "html-marquee"], [2])


if __name__ == "__main__":
    unittest.main()
