"""Tests for rule-set loading, validation and baseline parsing."""

import json
import tempfile
import unittest
from pathlib import Path

from baselineguard.rules import (
    RuleSetError,
    load_default_ruleset,
    load_ruleset,
    parse_baseline,
    validate_ruleset,
)


class DefaultRulesetTests(unittest.TestCase):
    def test_bundled_ruleset_is_valid(self):
        rs = load_default_ruleset()
        self.assertEqual(rs.source, "builtin")
        self.assertEqual(rs.version, "1.0.0")
        self.assertGreaterEqual(len(rs.rules), 40)
        self.assertEqual(len(rs.rules), len(rs.by_id), "rule ids must be unique")

    def test_every_status_is_represented(self):
        rs = load_default_ruleset()
        self.assertEqual({r.status for r in rs.rules}, {"widely", "newly", "limited", "deprecated"})

    def test_limited_and_deprecated_have_no_baseline_year(self):
        rs = load_default_ruleset()
        for r in rs.rules:
            if r.status in ("limited", "deprecated"):
                self.assertIsNone(r.baseline_year)

    def test_all_patterns_compile(self):
        import re
        for r in load_default_ruleset().rules:
            for pattern in r.patterns:
                with self.subTest(rule=r.id, pattern=pattern):
                    re.compile(pattern)


class ValidationTests(unittest.TestCase):
    def _one_rule(self, **overrides):
        rule = {
            "id": "custom-rule", "name": "Custom", "category": "css",
            "status": "widely", "baseline_year": 2020, "applies_to": ["css"],
            "patterns": ["custom\\s*\\("], "suggestion": "Do X", "reference": "https://example.com",
        }
        rule.update(overrides)
        return {"rules": [rule]}

    def test_valid_document(self):
        self.assertEqual(validate_ruleset(self._one_rule()), [])

    def test_rejects_missing_field(self):
        doc = self._one_rule()
        del doc["rules"][0]["suggestion"]
        self.assertTrue(validate_ruleset(doc))

    def test_rejects_bad_status(self):
        doc = self._one_rule(status="unknown")
        self.assertTrue(any("status" in e for e in validate_ruleset(doc)))

    def test_rejects_bad_regex(self):
        doc = self._one_rule(patterns=["[unterminated"])
        self.assertTrue(any("invalid regex" in e for e in validate_ruleset(doc)))

    def test_rejects_duplicate_ids(self):
        doc = self._one_rule()
        doc["rules"].append(dict(doc["rules"][0]))
        self.assertTrue(any("duplicate" in e for e in validate_ruleset(doc)))

    def test_rejects_bad_mode(self):
        doc = self._one_rule()
        doc["mode"] = "merge"
        self.assertTrue(any("mode" in e for e in validate_ruleset(doc)))

    def test_rejects_non_object_root(self):
        self.assertTrue(validate_ruleset([]))


class CustomRulesetTests(unittest.TestCase):
    def test_replace_mode_uses_only_custom_rules(self):
        doc = {
            "name": "mine", "version": "2.0.0", "mode": "replace",
            "rules": [{
                "id": "css-grid", "name": "Grid (custom)", "category": "css",
                "status": "deprecated", "baseline_year": None, "applies_to": ["css"],
                "patterns": ["display\\s*:\\s*grid"], "suggestion": "ban it",
                "reference": "https://example.com",
            }],
        }
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.json"
            p.write_text(json.dumps(doc), encoding="utf-8")
            rs = load_ruleset(str(p))
        self.assertEqual(len(rs.rules), 1)
        self.assertEqual(rs.get("css-grid").status, "deprecated")

    def test_extend_mode_overrides_one_rule(self):
        base = load_default_ruleset()
        doc = {"mode": "extend", "rules": [{
            "id": "css-grid", "name": "Grid (overridden)", "category": "css",
            "status": "newly", "baseline_year": 2024, "applies_to": ["css"],
            "patterns": ["display\\s*:\\s*grid"], "suggestion": "review",
            "reference": "https://example.com",
        }]}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.json"
            p.write_text(json.dumps(doc), encoding="utf-8")
            rs = load_ruleset(str(p))
        self.assertEqual(len(rs.rules), len(base.rules))
        self.assertEqual(rs.get("css-grid").status, "newly")
        self.assertEqual(rs.get("css-has").status, "newly")

    def test_missing_file_raises(self):
        with self.assertRaises(RuleSetError):
            load_ruleset("/definitely/not/here.json")


class BaselineParsingTests(unittest.TestCase):
    def test_presets(self):
        self.assertEqual(parse_baseline("widely"), (2021, "widely"))
        self.assertEqual(parse_baseline("NEWLY"), (2024, "newly"))
        self.assertEqual(parse_baseline("limited"), (9999, "limited"))

    def test_year(self):
        self.assertEqual(parse_baseline("2023"), (2023, "2023"))

    def test_invalid(self):
        for bad in ("20xx", "1899", "next", ""):
            with self.subTest(bad=bad), self.assertRaises(RuleSetError):
                parse_baseline(bad)


if __name__ == "__main__":
    unittest.main()
