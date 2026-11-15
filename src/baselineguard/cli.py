"""Command line interface for BaselineGuard."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Optional

from . import __version__
from .context import DEFAULT_OUTPUTS, FORMATS, build_context, write_context
from .detector import detect, iter_files
from .render import render_json, render_markdown, render_text
from .rules import RuleSetError, load_ruleset, parse_baseline, validate_ruleset
from .verdict import Policy, build_report, evaluate


class UsageError(ValueError):
    """User-facing CLI error -> exit code 2."""


def _policy(args: argparse.Namespace) -> Policy:
    year, label = parse_baseline(args.baseline)
    return Policy(
        baseline_year=year,
        baseline_label=label,
        allow_newly=getattr(args, "allow_newly", False),
        allow_limited=getattr(args, "allow_limited", False),
        fail_on=getattr(args, "fail_on", "error"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="baselineguard",
        description=(
            "Offline, zero-dependency Web platform Baseline guard. "
            "Scan source code for feature usage and generate AI coding-agent policy context."
        ),
        epilog=(
            "examples:\n"
            "  baselineguard scan . --baseline 2021\n"
            "  baselineguard scan src --format json --fail-on warning -o report.json\n"
            "  baselineguard context --baseline 2023 --format agents-md --out AGENTS.md\n"
            "  baselineguard rules validate examples/custom-rules.json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"BaselineGuard {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    # ---- scan ----
    scan = sub.add_parser("scan", help="scan a file or directory for Web feature usage")
    scan.add_argument("path", nargs="?", default=".", help="file or directory (default: .)")
    scan.add_argument("--baseline", default="widely",
                      help="target Baseline: a year (e.g. 2021) or widely/newly/limited (default: widely)")
    scan.add_argument("--rules", help="custom rule set JSON (replace, or extend with \"mode\": \"extend\")")
    scan.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    scan.add_argument("--fail-on", choices=("error", "warning", "none"), default="error",
                      help="which severity makes the command exit 1 (default: error)")
    scan.add_argument("--allow-newly", action="store_true", help="downgrade newly-available features to info")
    scan.add_argument("--allow-limited", action="store_true", help="downgrade limited features to warning")
    scan.add_argument("--include", action="append", default=[], metavar="GLOB",
                      help="only scan matching relative paths (repeatable)")
    scan.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                      help="skip matching relative paths (repeatable)")
    scan.add_argument("--include-docs", action="store_true", help="also scan Markdown/MDX files")
    scan.add_argument("--no-ignore", action="store_true", help="do not skip node_modules/dist/.git etc.")
    scan.add_argument("-o", "--output", help="write the report to a file instead of stdout")
    scan.add_argument("--quiet", action="store_true", help="suppress stdout (still honours --output)")

    # ---- context ----
    ctx = sub.add_parser("context", help="generate an AI coding-agent policy file")
    ctx.add_argument("--baseline", default="widely", help="target Baseline year or preset")
    ctx.add_argument("--rules", help="custom rule set JSON")
    ctx.add_argument("--format", choices=FORMATS, default="agents-md")
    ctx.add_argument("--out", help=f"output path (default depends on --format: {DEFAULT_OUTPUTS})")
    ctx.add_argument("--allow-newly", action="store_true")
    ctx.add_argument("--allow-limited", action="store_true")
    ctx.add_argument("--stdout", action="store_true", help="print to stdout instead of writing a file")

    # ---- rules ----
    rules = sub.add_parser("rules", help="inspect or validate rule sets")
    rsub = rules.add_subparsers(dest="action", required=True)
    rlist = rsub.add_parser("list", help="list rules")
    rlist.add_argument("--rules", help="custom rule set JSON")
    rlist.add_argument("--status", choices=("widely", "newly", "limited", "deprecated"))
    rlist.add_argument("--format", choices=("text", "json"), default="text")
    rshow = rsub.add_parser("show", help="show one rule")
    rshow.add_argument("rule_id")
    rshow.add_argument("--rules", help="custom rule set JSON")
    rval = rsub.add_parser("validate", help="validate a rule set file without loading the defaults")
    rval.add_argument("file")

    return parser


def _write(text: str, output: Optional[str], quiet: bool) -> None:
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text.rstrip("\n") + "\n", encoding="utf-8")
    if not quiet:
        print(text)


def _cmd_scan(args: argparse.Namespace) -> int:
    root = Path(args.path)
    if not root.exists():
        raise UsageError(f"path does not exist: {args.path}")
    ruleset = load_ruleset(args.rules)
    policy = _policy(args)
    started = time.monotonic()
    files = list(iter_files(
        root,
        includes=args.include,
        excludes=args.exclude,
        include_docs=args.include_docs,
        use_default_ignores=not args.no_ignore,
    ))
    hits, files_scanned, lines_scanned = detect(files, ruleset)
    findings = evaluate(hits, ruleset, policy)
    duration_ms = int((time.monotonic() - started) * 1000)
    report = build_report(
        ruleset=ruleset,
        policy=policy,
        findings=findings,
        root=str(root),
        files_scanned=files_scanned,
        lines_scanned=lines_scanned,
        duration_ms=duration_ms,
    )
    renderer = {"text": render_text, "json": render_json, "markdown": render_markdown}[args.format]
    _write(renderer(report), args.output, args.quiet)
    return report["exit_code"]


def _cmd_context(args: argparse.Namespace) -> int:
    ruleset = load_ruleset(args.rules)
    policy = _policy(args)
    content = build_context(ruleset, policy, args.format)
    if args.stdout:
        print(content)
        return 0
    out = Path(args.out or DEFAULT_OUTPUTS[args.format])
    status = write_context(out, content, args.format)
    print(f"context {status}: {out} "
          f"(allow/review/deny policy for {len(ruleset.rules)} rules, baseline {policy.baseline_label})")
    return 0


def _cmd_rules(args: argparse.Namespace) -> int:
    if args.action == "validate":
        p = Path(args.file)
        if not p.is_file():
            raise UsageError(f"rule set file not found: {args.file}")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"INVALID: {args.file}\n  - not valid JSON: {exc}")
            return 1
        errors = validate_ruleset(data)
        if errors:
            print(f"INVALID: {args.file}\n  - " + "\n  - ".join(errors))
            return 1
        print(f"VALID: {args.file} ({len(data['rules'])} rules, mode={data.get('mode', 'replace')})")
        return 0

    ruleset = load_ruleset(getattr(args, "rules", None))
    if args.action == "show":
        rule = ruleset.get(args.rule_id)
        if rule is None:
            raise UsageError(f"unknown rule id: {args.rule_id}")
        print(json.dumps({
            "id": rule.id, "name": rule.name, "category": rule.category,
            "status": rule.status, "baseline_year": rule.baseline_year,
            "applies_to": list(rule.applies_to), "patterns": list(rule.patterns),
            "suggestion": rule.suggestion, "reference": rule.reference,
        }, indent=2, ensure_ascii=False))
        return 0

    # list
    rules: List = [r for r in ruleset.rules if not args.status or r.status == args.status]
    if args.format == "json":
        print(json.dumps([{
            "id": r.id, "name": r.name, "category": r.category, "status": r.status,
            "baseline_year": r.baseline_year, "applies_to": list(r.applies_to),
            "patterns": list(r.patterns), "suggestion": r.suggestion, "reference": r.reference,
        } for r in rules], indent=2, ensure_ascii=False))
    else:
        print(f"{'ID':<32} {'STATUS':<12} {'YEAR':<6} {'CATEGORY':<9} NAME")
        print("-" * 100)
        for r in rules:
            year = str(r.baseline_year) if r.baseline_year is not None else "-"
            print(f"{r.id:<32} {r.status:<12} {year:<6} {r.category:<9} {r.name}")
        print(f"\n{len(rules)} rules from {ruleset.name} {ruleset.version} ({ruleset.source})")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            return _cmd_scan(args)
        if args.command == "context":
            return _cmd_context(args)
        if args.command == "rules":
            return _cmd_rules(args)
        raise UsageError(f"unknown command: {args.command}")  # pragma: no cover
    except (UsageError, RuleSetError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
