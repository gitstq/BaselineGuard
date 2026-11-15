#!/usr/bin/env bash
# A reproducible 60-second demo: scan + JSON report + generated agent context.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export PYTHONPATH=src

echo "== 1. scan (human-readable) =="
"$PY" -m baselineguard scan tests/fixtures --baseline widely --fail-on none

echo
echo "== 2. scan (machine-readable) =="
"$PY" -m baselineguard scan tests/fixtures --format json --fail-on none \
  | "$PY" -c "import json,sys; r=json.load(sys.stdin); print('files=%d lines=%d error=%d warning=%d info=%d' % (r['scan']['files_scanned'], r['scan']['lines_scanned'], r['counts']['error'], r['counts']['warning'], r['counts']['info']))"

echo
echo "== 3. generate AI agent policy (preview) =="
"$PY" -m baselineguard context --format agents-md --stdout | head -30

echo
echo "== 4. custom rule set validation =="
"$PY" -m baselineguard rules validate examples/custom-rules.json
