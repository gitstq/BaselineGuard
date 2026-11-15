# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-15

### Added

- 🎉 Initial release: offline, zero-dependency Web platform Baseline guard.
- 📚 Built-in versioned rule set with **41 rules** across four statuses
  (`widely` / `newly` / `limited` / `deprecated`) covering CSS, HTML and JS/Web APIs.
- 🔍 `scan` command: recursive source discovery, comment masking that preserves
  line/column numbers, same-line deduplication, and `text` / `json` / `markdown` reports.
- 🚦 Policy engine: `--baseline YEAR|widely|newly|limited`, `--allow-newly`,
  `--allow-limited`, `--fail-on error|warning|none` with meaningful CI exit codes.
- 🤖 `context` command: generates `AGENTS.md`, `CLAUDE.md`, `.cursorrules` or plain
  Markdown policy blocks with **idempotent marker-based insertion**.
- 🧩 `rules list|show|validate` plus user rule sets in `replace` or `extend` mode.
- 📦 `scripts/build.sh` produces a single-file `dist/baselineguard.pyz` zipapp with
  no compiler and no wheels.
- ✅ 45+ unit tests covering rules, detection, policy, context generation and the CLI.
- 🌐 Trilingual README (简体中文 / 繁體中文 / English) and GitHub Actions CI across
  Python 3.9 - 3.13.

### Notes

- BaselineGuard is a **library / CLI tool**, not a desktop application, so no
  platform binaries or GitHub Release assets are shipped. Installation and
  integration steps are documented in the README instead.
- `baseline_year` values are a maintained community snapshot used for policy
  cropping, not authoritative compatibility claims. Override them with `--rules`.
