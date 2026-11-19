#!/bin/bash
# Double-click to start Mockup Workflow in the browser.
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Installing dependencies (first run only)..."
  python3 -m venv .venv && .venv/bin/python -m pip install -q --upgrade pip && .venv/bin/pip install -q -r requirements.txt || exit 1
fi
(sleep 2 && open "http://127.0.0.1:5173") &
exec .venv/bin/python app.py
