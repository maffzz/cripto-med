#!/usr/bin/env python3
"""
Script para generar una llave criptográfica AES-256 (32 bytes) codificada en base64url.
Estándares: FIPS 197 / NIST SP 800-38D.
"""

import base64
import secrets

def generate_key_b64url() -> str:
    key_bytes = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(key_bytes).decode("ascii").rstrip("=")

if __name__ == "__main__":
    print(generate_key_b64url())
