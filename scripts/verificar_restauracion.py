#!/usr/bin/env bash
"""": # Bash wrapper para delegar al contenedor Docker si se ejecuta en el host
if command -v docker >/dev/null 2>&1 && [ ! -f /.dockerenv ]; then
  exec docker compose run --rm backend python scripts/verificar_restauracion.py "$@"
fi
exec python3 "$0" "$@"
"""
import sys
from pathlib import Path

backend_script = Path(__file__).resolve().parent.parent / "backend" / "scripts" / "verificar_restauracion.py"
if not backend_script.exists():
    backend_script = Path(__file__).resolve().parent / "verificar_restauracion.py"

exec(open(backend_script).read())
