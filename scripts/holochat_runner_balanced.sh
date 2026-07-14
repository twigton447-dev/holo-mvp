#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$ROOT/.venv312/bin/python" "$ROOT/scripts/holochat_experiment_runner.py" \
  --lane balanced --condition D --rotations 8 "$@"
