"""Tests for policy classification, exit codes and report assembly."""

import unittest

from baselineguard.detector import Hit
from baselineguard.rules import Rule, load_default_ruleset
from baselineguard.verdict import Policy, build_report, classify, compute_exit_code, evaluate


def make_rule(status, year=None):
    return Rule(
        id="x-" + status, name="X", category="css", status=status,
        baseline_year=year, applies_to=("css",), patterns=("x",),
        suggestion="fix", reference="https://example.com",
    )


class ClassifyTests(unittest.TestCase):
    def setUp(self):
        self.p = Policy(2021, "widely")

    def test_deprecated_is_always_error(self):
        relaxed = Policy(9999, "limited", allow_newly=True, allow_limited=True)
        self.assertEqual(classify(make_rule("deprecated"), relaxed)[0], "error")

    def test_limited_error_unless_allowed(self):
        self.assertEqual(classify(make_rule("limited"), self.p)[0], "error")
        self.assertEqual(classify(make_rule("limited"), Policy(2021, "widely", allow_limited=True))[0], "warning")

    def test_newly_warning_unless_allowed(self):
        self.assertEqual(classify(make_rule("newly", 2023), self.p)[0], "warning")
        self.assertEqual(classify(make_rule("newly", 2023), Policy(2021, "widely", allow_newly=True))[0], "info")

    def test_widely_inside_baseline_is_info(self):
        self.assertEqual(classify(make_rule("widely", 2020), self.p)[0], "info")

    def test_widely_after_baseline_is_warning(self):
        self.assertEqual(classify(make_rule("widely", 2024), self.p)[0], "warning")

    def test_year_does_not_auto_allow_newly(self):
        p = Policy(2025, "2025")
        self.assertEqual(classify(make_rule("newly", 2023), p)[0], "warning")


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.rs = load_default_ruleset()

    def _findings(self, ids, policy):
        hits = [Hit(rule_id=i, path="a.css", line=1, column=1, snippet="x", matched="x") for i in ids]
        return evaluate(hits, self.rs, policy)

    def test_exit_code_error_policy(self):
        p = Policy(2021, "widely", fail_on="error")
        f = self._findings(["html-marquee", "css-has"], p)
        self.assertEqual(compute_exit_code(f, p), 1)

    def test_exit_code_warning_policy(self):
        p = Policy(2021, "widely", fail_on="warning")
        f = self._findings(["css-has"], p)
        self.assertEqual(compute_exit_code(f, p), 1)

    def test_exit_code_none(self):
        p = Policy(2021, "widely", fail_on="none")
        f = self._findings(["html-marquee"], p)
        self.assertEqual(compute_exit_code(f, p), 0)

    def test_findings_sorted_by_severity(self):
        p = Policy(2021, "widely")
        f = self._findings(["css-flexbox", "css-has", "html-marquee"], p)
        self.assertEqual([x.severity for x in f], ["error", "warning", "info"])

    def test_build_report_shape(self):
        p = Policy(2021, "widely")
        f = self._findings(["html-marquee", "css-has"], p)
        r = build_report(ruleset=self.rs, policy=p, findings=f, root=".",
                         files_scanned=3, lines_scanned=42, duration_ms=7)
        self.assertEqual(r["counts"]["total"], 2)
        self.assertEqual(r["counts"]["error"], 1)
        self.assertEqual(r["counts"]["warning"], 1)
        self.assertEqual(r["exit_code"], 1)
        self.assertFalse(r["passed"])
        self.assertEqual(r["scan"]["files_scanned"], 3)
        self.assertEqual(len(r["findings"]), 2)
        self.assertIn("reference", r["findings"][0])


if __name__ == "__main__":
    unittest.main()
