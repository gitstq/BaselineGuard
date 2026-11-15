# Contributing to BaselineGuard

Thanks for helping make the web a little more predictable. 🙌

## Ground rules

- **Zero dependencies.** Any change that adds a third-party runtime dependency will be declined. The standard library is the whole point.
- **Offline first.** No network calls at scan time, ever.
- **Python 3.9+ compatible.** Do not use syntax or APIs introduced after 3.9.
- **No copied code.** Rules and documentation may reference public specifications, but implementation must be original.

## Development loop

```bash
git clone https://github.com/gitstq/BaselineGuard.git
cd BaselineGuard
bash scripts/test.sh          # full unit tests
bash scripts/demo.sh          # reproducible demo
bash scripts/build.sh         # dist/baselineguard.pyz
```

## Adding or changing a rule

1. Edit `src/baselineguard/data/rules.json`. Every rule needs all nine fields
   described in `examples/README.md`.
2. Validate it: `PYTHONPATH=src python3 -m baselineguard rules validate src/baselineguard/data/rules.json`.
3. Add a fixture line in `tests/fixtures/` **and** an assertion in
   `tests/test_detector.py` so the detection is covered.
4. Bump `ruleset.version` when rule semantics change, and note it in `CHANGELOG.md`.

Regexes should be specific enough to avoid false positives. Comments are
masked before matching (see `detector.strip_comments`), so new patterns do not
need to handle comments themselves.

## Commit messages (Angular convention)

```
feat: add detection for CSS anchor positioning
fix: avoid matching URLs in whole-line JS comments
docs: clarify the --allow-newly semantics
test: cover custom rule set extend mode
refactor: split renderers into a dedicated module
chore: bump ruleset to 1.1.0
```

## Pull requests

- Keep one concern per PR.
- Include the output of `bash scripts/test.sh` in the description.
- Update all three language sections of `README.md` if user-facing behaviour changes; `DocConcord`-style parity matters here.
- Do not commit generated reports, `.env` files, tokens, or `dist/*.pyz`.

## Issues

Please include: command used, `--format json` report (redacted as needed),
Python version, OS, and a minimal source snippet that reproduces the finding.
