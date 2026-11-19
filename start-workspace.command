#!/bin/bash
set -e
cd "$(dirname "$0")"
if command -v uv >/dev/null 2>&1; then
  exec uv run reproscout serve "$@"
fi
if [ -x .venv/bin/reproscout ]; then
  exec .venv/bin/reproscout serve "$@"
fi
printf '%s\n' 'Install uv and run uv sync --locked --extra dev, then start this launcher again.'
exit 1
