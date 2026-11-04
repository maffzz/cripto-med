"""
Pruebas unitarias para el módulo de criptografía AES-256-GCM (app/crypto.py).
Estándares verificados:
- FIPS 197 / NIST SP 800-38D (AES-GCM 256 bits).
- NIST SP 800-57 Part 1 (Gestión de llaves).
"""

import sys
from pathlib import Path

# Asegurar backend en sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from backend.tests.test_crypto import *
