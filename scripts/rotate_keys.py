#!/usr/bin/env python3
"""Wrapper para backend/scripts/rotate_keys.py"""
import sys
from pathlib import Path

backend_script = Path(__file__).resolve().parent.parent / "backend" / "scripts" / "rotate_keys.py"
if not backend_script.exists():
    backend_script = Path(__file__).resolve().parent / "rotate_keys.py"

exec(open(backend_script).read())
