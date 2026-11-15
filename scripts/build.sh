#!/usr/bin/env bash
# Build a single-file, dependency-free zipapp: dist/baselineguard.pyz
# Works on Windows (Git Bash / WSL), macOS and Linux: no compiler, no wheels.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
STAGE="build/zipapp"

rm -rf "$STAGE"
mkdir -p "$STAGE/baselineguard" dist
cp -R src/baselineguard/. "$STAGE/baselineguard/"
cp scripts/zipapp_main.py "$STAGE/__main__.py"
find "$STAGE" -type d -name '__pycache__' -prune -exec rm -rf {} +

"$PY" -m zipapp "$STAGE" -o dist/baselineguard.pyz -p "/usr/bin/env python3"

# Smoke test the artefact itself.
VERSION="$("$PY" dist/baselineguard.pyz --version)"
echo "built dist/baselineguard.pyz -> $VERSION"
