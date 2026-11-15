"""Baseline policy evaluation and report construction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple

from . import __version__
from .detector import Hit
from .rules import Rule, Ruleset


@dataclass(frozen=True)
class Policy:
    baseline_year: int
    baseline_label: str
    allow_newly: bool = False
    allow_limited: bool = False
    fail_on: str = "error"  # error | warning | none

    def as_dict(self) -> Dict:
        return {
            "baseline_year": self.baseline_year,
            "baseline_label": self.baseline_label,
            "allow_newly": self.allow_newly,
            "allow_limited": self.allow_limited,
            "fail_on": self.fail_on,
        }


@dataclass(frozen=True)
class Finding:
    rule_id: str
    rule_name: str
    category: str
    status: str
    severity: str
    path: str
    line: int
    column: int
    snippet: str
    matched: str
    reason: str
    suggestion: str
    reference: str


def classify(rule: Rule, policy: Policy) -> Tuple[str, str]:
    """Return (severity, reason) for a rule under the given policy."""
    if rule.status == "deprecated":
        return "error", "Deprecated or removed Web feature; must not appear in new code."
    if rule.status == "limited":
        if policy.allow_limited:
            return "warning", "Limited availability, explicitly downgraded by --allow-limited; a fallback is still required."
        return "error", "Limited availability: not supported in all four major engines yet."
    if rule.status == "newly":
        if policy.allow_newly:
            return "info", "Newly available, explicitly allowed by --allow-newly."
        return "warning", "Newly available but not yet Widely Baseline; confirm a degradation path."
    # widely
    if rule.baseline_year is not None and rule.baseline_year <= policy.baseline_year:
        return "info", "Widely available within the target Baseline year."
    return "warning", "Widely available only after the target Baseline year."


def evaluate(hits: List[Hit], ruleset: Ruleset, policy: Policy) -> List[Finding]:
    by_id = ruleset.by_id
    findings: List[Finding] = []
    for hit in hits:
        rule = by_id.get(hit.rule_id)
        if rule is None:  # pragma: no cover - defensive
            continue
        severity, reason = classify(rule, policy)
        findings.append(Finding(
            rule_id=rule.id,
            rule_name=rule.name,
            category=rule.category,
            status=rule.status,
            severity=severity,
            path=hit.path,
            line=hit.line,
            column=hit.column,
            snippet=hit.snippet,
            matched=hit.matched,
            reason=reason,
            suggestion=rule.suggestion,
            reference=rule.reference,
        ))
    order = {"error": 0, "warning": 1, "info": 2}
    findings.sort(key=lambda f: (order[f.severity], f.path, f.line, f.rule_id))
    return findings


def compute_exit_code(findings: List[Finding], policy: Policy) -> int:
    if policy.fail_on == "none":
        return 0
    if policy.fail_on == "warning":
        return 1 if any(f.severity in ("error", "warning") for f in findings) else 0
    return 1 if any(f.severity == "error" for f in findings) else 0


def build_report(
    *,
    ruleset: Ruleset,
    policy: Policy,
    findings: List[Finding],
    root: str,
    files_scanned: int,
    lines_scanned: int,
    duration_ms: int,
) -> Dict:
    counts = {s: sum(1 for f in findings if f.severity == s) for s in ("error", "warning", "info")}
    exit_code = compute_exit_code(findings, policy)
    return {
        "schema_version": 1,
        "tool": "BaselineGuard",
        "version": __version__,
        "policy": policy.as_dict(),
        "ruleset": {
            "name": ruleset.name,
            "version": ruleset.version,
            "source": ruleset.source,
            "rule_count": len(ruleset.rules),
        },
        "scan": {
            "root": root,
            "files_scanned": files_scanned,
            "lines_scanned": lines_scanned,
            "duration_ms": duration_ms,
        },
        "counts": {**counts, "total": len(findings)},
        "findings": [asdict(f) for f in findings],
        "passed": exit_code == 0,
        "exit_code": exit_code,
    }
