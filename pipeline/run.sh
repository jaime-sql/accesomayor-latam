#!/usr/bin/env bash
# One-command audit: ./run.sh FRAME.csv OUTDIR [--limit N] [--ids SV-001,...]
set -euo pipefail
cd "$(dirname "$0")"; HERE=$PWD
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
npm ci --silent
CH=browsers/chrome/linux-131.0.6778.204/chrome-linux64/chrome
[ -x "$CH" ] || npx @puppeteer/browsers install chrome@131.0.6778.204 --path "$HERE/browsers"
FRAME=$(realpath "$1"); OUT=$(realpath -m "$2"); shift 2
.venv/bin/python audit.py "$FRAME" "$OUT" "$@"
