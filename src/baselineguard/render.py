"""Renderers for text (terminal), JSON (machines) and Markdown (PR/CI)."""

from __future__ import annotations

import json
from typing import Dict, List

SEVERITY_MARK = {"error": "[X]", "warning": "[!]", "info": "[i]"}
SEVERITY_TITLE = {
    "error": "ERROR   - violations that break the policy",
    "warning": "WARNING - features requiring an explicit decision",
    "info": "INFO    - features inside the allowed Baseline",
}


def _header_zh_en(report: Dict) -> str:
    p = report["policy"]
    r = report["ruleset"]
    s = report["scan"]
    return (
        f"BaselineGuard {report['version']} | offline Web platform Baseline guard\n"
        f"Target : {p['baseline_label']} (widely <= {p['baseline_year']}) "
        f"| allow-newly={str(p['allow_newly']).lower()} "
        f"allow-limited={str(p['allow_limited']).lower()} fail-on={p['fail_on']}\n"
        f"Ruleset: {r['name']} {r['version']} ({r['rule_count']} rules, {r['source']})\n"
        f"Scan   : {s['files_scanned']} files / {s['lines_scanned']} lines "
        f"in {s['duration_ms']} ms | root={s['root']}"
    )


def render_text(report: Dict) -> str:
    lines: List[str] = [_header_zh_en(report), ""]
    counts = report["counts"]
    if not report["findings"]:
        lines.append("No Web platform features matched the rule set. Nothing to report.")
    for severity in ("error", "warning", "info"):
        group = [f for f in report["findings"] if f["severity"] == severity]
        if not group:
            continue
        lines.append(f"{SEVERITY_MARK[severity]} {SEVERITY_TITLE[severity]} ({len(group)})")
        for f in group:
            lines.append(f"  [{f['rule_id']}] {f['rule_name']}  ({f['status']})")
            lines.append(f"    {f['path']}:{f['line']}:{f['column']}  {f['snippet']}")
            lines.append(f"    why      : {f['reason']}")
            lines.append(f"    action   : {f['suggestion']}")
            lines.append(f"    reference: {f['reference']}")
        lines.append("")
    c = report["counts"]
    verdict = "PASSED" if report["passed"] else "FAILED"
    lines.append(
        f"Result : {verdict}  "
        f"(error={c['error']}, warning={c['warning']}, info={c['info']}, "
        f"total={c['total']})  exit={report['exit_code']}"
    )
    return "\n".join(lines)


def render_json(report: Dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=False)


def render_markdown(report: Dict) -> str:
    p, r, s, c = report["policy"], report["ruleset"], report["scan"], report["counts"]
    out: List[str] = [
        "## BaselineGuard report",
        "",
        f"**Result:** {'PASSED' if report['passed'] else 'FAILED'} &nbsp;|&nbsp; "
        f"**Target:** `{p['baseline_label']}` (widely &le; {p['baseline_year']}) &nbsp;|&nbsp; "
        f"**Ruleset:** `{r['name']} {r['version']}` ({r['rule_count']} rules)",
        "",
        f"Scanned **{s['files_scanned']}** files / **{s['lines_scanned']}** lines in {s['duration_ms']} ms. "
        f"Findings: **{c['error']}** error, **{c['warning']}** warning, **{c['info']}** info.",
        "",
    ]
    if not report["findings"]:
        out += ["_No Web platform features matched the rule set._", ""]
        return "\n".join(out)
    out += [
        "| Severity | Rule | Status | Location | Why | Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for f in report["findings"]:
        out.append(
            f"| {f['severity'].upper()} | `{f['rule_id']}` | {f['status']} | "
            f"`{f['path']}:{f['line']}` | {f['reason']} | {f['suggestion']} |"
        )
    out.append("")
    return "\n".join(out)
