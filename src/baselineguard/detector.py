"""Source-code scanning: file discovery, comment masking and feature detection.

Everything here is pure standard library. No network access, no third-party
parsers: detection is regex based, which keeps the tool offline-first and
fast enough to run on every commit.
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, FrozenSet, Iterable, Iterator, List, Tuple

from .rules import Ruleset

EXT_CATEGORIES: Dict[str, FrozenSet[str]] = {
    ".css": frozenset({"css"}),
    ".scss": frozenset({"css"}),
    ".less": frozenset({"css"}),
    ".html": frozenset({"markup", "css", "script"}),
    ".htm": frozenset({"markup", "css", "script"}),
    ".vue": frozenset({"markup", "css", "script"}),
    ".svelte": frozenset({"markup", "css", "script"}),
    ".astro": frozenset({"markup", "css", "script"}),
    ".js": frozenset({"script"}),
    ".mjs": frozenset({"script"}),
    ".cjs": frozenset({"script"}),
    ".jsx": frozenset({"script"}),
    ".ts": frozenset({"script"}),
    ".tsx": frozenset({"script"}),
    ".mts": frozenset({"script"}),
    ".cts": frozenset({"script"}),
    ".md": frozenset({"doc"}),
    ".mdx": frozenset({"doc"}),
}

DEFAULT_IGNORE_DIRS = frozenset({
    ".git", "node_modules", "dist", "build", "out", "vendor", ".venv", "venv",
    "__pycache__", ".next", ".nuxt", "coverage", "target", ".idea", ".vscode",
    "site-packages", ".cache", ".turbo", ".svelte-kit", ".parcel-cache",
})

MAX_FILE_BYTES = 2 * 1024 * 1024  # skip generated bundles / minified blobs


@dataclass(frozen=True)
class Hit:
    rule_id: str
    path: str
    line: int
    column: int
    snippet: str
    matched: str


def _blank(match: "re.Match") -> str:
    """Replace a comment with same-length spaces, preserving newlines."""
    return re.sub(r"[^\n]", " ", match.group(0))


def strip_comments(text: str, is_pure_script: bool) -> str:
    """Mask comments so that line/column numbers stay identical to the source."""
    text = re.sub(r"<!--.*?-->", _blank, text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", _blank, text, flags=re.S)
    if is_pure_script:
        # Conservative: only whole-line // comments, so URLs like https:// survive.
        text = re.sub(r"(?m)^[ \t]*//[^\n]*", _blank, text)
    return text


def _matches_globs(rel: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(Path(rel).name, p) for p in patterns)


def iter_files(
    root: Path,
    includes: Iterable[str] = (),
    excludes: Iterable[str] = (),
    include_docs: bool = False,
    use_default_ignores: bool = True,
) -> Iterator[Tuple[Path, FrozenSet[str], str]]:
    """Yield (absolute path, categories, repo-relative path)."""
    includes, excludes = list(includes), list(excludes)
    if root.is_file():
        cats = EXT_CATEGORIES.get(root.suffix.lower())
        if cats and (include_docs or "doc" not in cats):
            yield root, cats, root.name
        return

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:  # pragma: no cover
            continue
        rel_parts = set(Path(rel).parts)
        if use_default_ignores and rel_parts & DEFAULT_IGNORE_DIRS:
            continue
        if excludes and _matches_globs(rel, excludes):
            continue
        cats = EXT_CATEGORIES.get(path.suffix.lower())
        if not cats:
            continue
        if "doc" in cats and not include_docs:
            continue
        if includes and not _matches_globs(rel, includes):
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:  # pragma: no cover
            continue
        yield path, cats, rel


def read_source(path: Path) -> str:
    """Read a source file defensively; never fail the whole scan on encoding."""
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")  # pragma: no cover


def detect(
    files: List[Tuple[Path, FrozenSet[str], str]],
    ruleset: Ruleset,
) -> Tuple[List[Hit], int, int]:
    """Return (hits, files_scanned, lines_scanned)."""
    compiled = []
    for rule in ruleset.rules:
        compiled.append((rule, [re.compile(p) for p in rule.patterns]))

    hits: List[Hit] = []
    seen = set()
    files_scanned = 0
    lines_scanned = 0

    for path, categories, rel in files:
        text = read_source(path)
        lines_scanned += text.count("\n") + (1 if text and not text.endswith("\n") else 0)
        files_scanned += 1
        is_pure_script = categories == frozenset({"script"})
        masked = strip_comments(text, is_pure_script)
        source_lines = text.splitlines()

        for rule, regexes in compiled:
            if not rule.applies_to_any(categories):
                continue
            for regex in regexes:
                for m in regex.finditer(masked):
                    key = (rule.id, rel, masked.count("\n", 0, m.start()) + 1)
                    if key in seen:
                        continue
                    seen.add(key)
                    line = key[2]
                    line_text = source_lines[line - 1] if 0 < line <= len(source_lines) else ""
                    hits.append(Hit(
                        rule_id=rule.id,
                        path=rel,
                        line=line,
                        column=m.start() - masked.rfind("\n", 0, m.start()),
                        snippet=line_text.strip()[:160],
                        matched=m.group(0)[:80],
                    ))
    hits.sort(key=lambda h: (h.path, h.line, h.rule_id))
    return hits, files_scanned, lines_scanned
