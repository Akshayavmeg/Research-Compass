#!/usr/bin/env bash
# ResearchCompass install script
set -e

echo "=== ResearchCompass Installation ==="

PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment (.venv)..."
  "$PYTHON_BIN" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip >/dev/null

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
fi

echo "Initializing faculty data and ChromaDB..."
python app.py init

echo ""
echo "=== Installation complete ==="
echo "Activate the environment with: source .venv/bin/activate"
echo "Then run:                       python app.py chat"
