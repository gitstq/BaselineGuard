#!/usr/bin/env bash
# Run the full unit-test suite without installing anything.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
PYTHONPATH=src "$PY" -m unittest discover -s tests -v
