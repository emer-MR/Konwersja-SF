#!/usr/bin/env bash
# Uruchamia konwerter SF w środowisku .venv (Linux).
# Bez argumentów -> GUI. Z argumentami -> przekazuje je do src/run.py (CLI).
#
# Odpowiednik windowsowego "Konwertuj SF.bat" dla trybu wsadowego:
#   .venv/bin/python src/konwertuj.py <pliki|folder>

set -euo pipefail
KATALOG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$KATALOG/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
    echo "Brak środowiska .venv w $KATALOG" >&2
    echo "Utwórz je poleceniem: uv venv --python 3.13 .venv && VIRTUAL_ENV=\$PWD/.venv uv pip install -r src/requirements.txt" >&2
    exit 1
fi

exec "$PY" "$KATALOG/src/run.py" "$@"
