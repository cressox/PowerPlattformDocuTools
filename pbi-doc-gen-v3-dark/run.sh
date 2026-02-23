#!/usr/bin/env bash
# Power BI Documentation Generator – Bash wrapper (macOS / Linux)
set -euo pipefail
cd "$(dirname "$0")"

# Find Python 3
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" --version 2>&1)
        if [[ "$ver" == Python\ 3* ]]; then
            PYTHON="$cmd"
            echo "✅ Gefunden: $ver"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    echo "❌ Python 3 nicht gefunden. Bitte installieren."
    exit 1
fi

# Install deps
if [[ -f requirements.txt ]]; then
    echo "📦 Prüfe Abhängigkeiten …"
    "$PYTHON" -m pip install -r requirements.txt --quiet 2>/dev/null || true
fi

echo ""
exec "$PYTHON" -m src.main
