"""Rule-set loading, validation and Baseline policy parsing.

A rule set is a plain, versioned JSON document. It can be shipped inside the
package (offline default) or supplied by the user with ``--rules``.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import STATUSES, SCANNABLE_CATEGORIES

DEFAULT_BASELINE_LABEL = "widely"
PRESET_BASELINES: Dict[str, int] = {
    # "widely" is deliberately conservative: features widely available by 2021.
    "widely": 2021,
    "newly": 2024,
    "limited": 9999,
}
MIN_YEAR, MAX_YEAR = 1995, 2100

REQUIRED_FIELDS = (
    "id", "name", "category", "status", "baseline_year",
    "applies_to", "patterns", "suggestion", "reference",
)


class RuleSetError(ValueError):
    """Raised when a rule set is malformed."""


@dataclass(frozen=True)
class Rule:
    id: str
    name: str
    category: str
    status: str
    baseline_year: Optional[int]
    applies_to: Tuple[str, ...]
    patterns: Tuple[str, ...]
    suggestion: str
    reference: str

    def applies_to_any(self, categories: frozenset) -> bool:
        return bool(set(self.applies_to) & set(categories))


@dataclass(frozen=True)
class Ruleset:
    schema_version: int
    name: str
    version: str
    description: str
    rules: Tuple[Rule, ...]
    source: str = "builtin"

    @property
    def by_id(self) -> Dict[str, Rule]:
        return {r.id: r for r in self.rules}

    def get(self, rule_id: str) -> Optional[Rule]:
        return self.by_id.get(rule_id)


def _validate_rule_dict(raw: Any, index: int) -> List[str]:
    errors: List[str] = []
    prefix = f"rules[{index}]"
    if not isinstance(raw, dict):
        return [f"{prefix}: expected an object"]
    for field in REQUIRED_FIELDS:
        if field not in raw:
            errors.append(f"{prefix}: missing field '{field}'")
    if errors:
        return errors

    if not isinstance(raw["id"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", raw["id"]):
        errors.append(f"{prefix}.id: must be a lowercase slug")
    if not isinstance(raw["name"], str) or not raw["name"].strip():
        errors.append(f"{prefix}.name: must be a non-empty string")
    if raw["status"] not in STATUSES:
        errors.append(f"{prefix}.status: must be one of {', '.join(STATUSES)}")
    year = raw["baseline_year"]
    if year is not None and (not isinstance(year, int) or isinstance(year, bool)):
        errors.append(f"{prefix}.baseline_year: must be an integer or null")
    if isinstance(year, int) and not MIN_YEAR <= year <= MAX_YEAR:
        errors.append(f"{prefix}.baseline_year: out of range {MIN_YEAR}-{MAX_YEAR}")
    applies = raw["applies_to"]
    if not isinstance(applies, list) or not applies or not all(a in SCANNABLE_CATEGORIES for a in applies):
        errors.append(f"{prefix}.applies_to: must be a non-empty list of {SCANNABLE_CATEGORIES}")
    patterns = raw["patterns"]
    if not isinstance(patterns, list) or not patterns or not all(isinstance(p, str) for p in patterns):
        errors.append(f"{prefix}.patterns: must be a non-empty list of regex strings")
    else:
        for j, pat in enumerate(patterns):
            try:
                re.compile(pat)
            except re.error as exc:
                errors.append(f"{prefix}.patterns[{j}]: invalid regex ({exc})")
    for field in ("suggestion", "reference", "category"):
        if not isinstance(raw[field], str) or not raw[field].strip():
            errors.append(f"{prefix}.{field}: must be a non-empty string")
    return errors


def validate_ruleset(data: Any) -> List[str]:
    """Return a list of human-readable validation errors (empty means valid)."""
    errors: List[str] = []
    if not isinstance(data, dict):
        return ["top level: expected an object"]
    if "rules" not in data or not isinstance(data["rules"], list) or not data["rules"]:
        return ["top level: 'rules' must be a non-empty array"]
    for i, raw in enumerate(data["rules"]):
        errors.extend(_validate_rule_dict(raw, i))
    ids = [r.get("id") for r in data["rules"] if isinstance(r, dict)]
    dupes = sorted({x for x in ids if x is not None and ids.count(x) > 1})
    if dupes:
        errors.append(f"duplicate rule ids: {', '.join(dupes)}")
    mode = data.get("mode", "replace")
    if mode not in ("replace", "extend"):
        errors.append("top level: 'mode' must be 'replace' or 'extend'")
    return errors


def _to_rule(raw: Dict[str, Any]) -> Rule:
    return Rule(
        id=raw["id"],
        name=raw["name"],
        category=raw["category"],
        status=raw["status"],
        baseline_year=raw["baseline_year"],
        applies_to=tuple(raw["applies_to"]),
        patterns=tuple(raw["patterns"]),
        suggestion=raw["suggestion"],
        reference=raw["reference"],
    )


def _from_document(data: Dict[str, Any], source: str) -> Ruleset:
    return Ruleset(
        schema_version=int(data.get("schema_version", 1)),
        name=str(data.get("name", source)),
        version=str(data.get("version", "0.0.0")),
        description=str(data.get("description", "")),
        rules=tuple(_to_rule(r) for r in data["rules"]),
        source=source,
    )


def load_default_ruleset() -> Ruleset:
    """Load the bundled offline rule set (works inside a zipapp too)."""
    resource = files("baselineguard") / "data" / "rules.json"
    data = json.loads(resource.read_text(encoding="utf-8"))
    errors = validate_ruleset(data)
    if errors:  # pragma: no cover - protects against a corrupted bundled file
        raise RuleSetError("bundled rule set is invalid: " + "; ".join(errors))
    return _from_document(data, "builtin")


def load_ruleset(path: Optional[str] = None) -> Ruleset:
    """Load the built-in rule set, or a user rule set that replaces/extends it."""
    if path is None:
        return load_default_ruleset()
    p = Path(path)
    if not p.is_file():
        raise RuleSetError(f"rule set file not found: {path}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuleSetError(f"rule set is not valid JSON: {exc}") from exc
    errors = validate_ruleset(data)
    if errors:
        raise RuleSetError("invalid rule set:\n  - " + "\n  - ".join(errors))
    custom = _from_document(data, str(p))
    if data.get("mode", "replace") == "replace":
        return custom
    base = load_default_ruleset()
    merged = {r.id: r for r in base.rules}
    merged.update({r.id: r for r in custom.rules})
    return Ruleset(
        schema_version=base.schema_version,
        name=base.name + "+custom",
        version=base.version,
        description=base.description,
        rules=tuple(merged.values()),
        source=custom.source,
    )


def parse_baseline(value: str) -> Tuple[int, str]:
    """Translate ``--baseline`` into a (year, label) pair."""
    v = str(value).strip().lower()
    if v in PRESET_BASELINES:
        return PRESET_BASELINES[v], v
    if re.fullmatch(r"(19|20)\d{2}", v):
        year = int(v)
        if MIN_YEAR <= year <= MAX_YEAR:
            return year, v
    raise RuleSetError(
        f"invalid baseline {value!r}: use a year {MIN_YEAR}-{MAX_YEAR} "
        f"or one of {', '.join(PRESET_BASELINES)}"
    )
