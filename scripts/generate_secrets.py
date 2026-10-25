#!/usr/bin/env python3
"""
Script para generar secretos nuevos para CriptoMed.
Imprime JWT_SECRET y contraseña de PostgreSQL, pero NO los escribe a disco.
"""

import secrets
import base64

def generate_jwt_secret():
    """Genera un JWT_SECRET nuevo (64 caracteres hex)."""
    return secrets.token_hex(32)

def generate_encryption_key():
    """Genera una llave Fernet nueva (AES-256)."""
    # Fernet key: 32 bytes base64 encoded
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

def generate_postgres_password():
    """Genera una contraseña segura para PostgreSQL."""
    # 16 caracteres: mayúsculas, minúsculas, dígitos
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(secrets.choice(alphabet) for _ in range(16))

if __name__ == "__main__":
    print("=== Generación de Secretos para CriptoMed ===")
    print()
    print("JWT_SECRET (para .env):")
    print(generate_jwt_secret())
    print()
    print("ENCRYPTION_KEY (para .env):")
    print(generate_encryption_key())
    print()
    print("POSTGRES_PASSWORD (para DATABASE_URL):")
    print(generate_postgres_password())
    print()
    print("⚠️  IMPORTANTE: Copia estos valores a tu .env local.")
    print("⚠️  NO los compartas ni los guardes en el repositorio.")
