#!/usr/bin/env python3
"""Wrapper para backend/scripts/verificar_cadena_logs.py"""
import sys
from pathlib import Path

backend_script = Path(__file__).resolve().parent.parent / "backend" / "scripts" / "verificar_cadena_logs.py"
if not backend_script.exists():
    backend_script = Path(__file__).resolve().parent / "verificar_cadena_logs.py"

exec(open(backend_script).read())
