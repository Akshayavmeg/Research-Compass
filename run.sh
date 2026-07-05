#!/usr/bin/env bash
# Convenience launcher for ResearchCompass.
set -e

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

python app.py chat
