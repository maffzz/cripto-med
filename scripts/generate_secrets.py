#!/usr/bin/env python3
"""
Script para generar secretos nuevos para CriptoMed.
Genera un .env completo a partir de .env.example con secretos aleatorios.
NO imprime los secretos en consola y se niega a sobrescribir un .env existente salvo con --force.
"""

import secrets
import base64
import os
import sys
from pathlib import Path

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

def generate_demo_password():
    """Genera una contraseña segura para usuarios de demo."""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$"
    return ''.join(secrets.choice(alphabet) for _ in range(12))

def generate_passphrase():
    """Genera una passphrase para backups."""
    words = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel"]
    return '-'.join(secrets.choice(words) for _ in range(4))

def generate_env_from_example():
    """Genera un .env completo a partir de .env.example con secretos aleatorios."""
    root_dir = Path(__file__).parent.parent
    env_example = root_dir / ".env.example"
    env_file = root_dir / ".env"
    
    if not env_example.exists():
        print(f"❌ Error: No existe {env_example}")
        sys.exit(1)
    
    if env_file.exists() and "--force" not in sys.argv:
        print(f"❌ Error: {env_file} ya existe. Usa --force para sobrescribir.")
        sys.exit(1)
    
    # Leer .env.example
    with open(env_example, 'r') as f:
        lines = f.readlines()
    
    # Generar secretos
    postgres_password = generate_postgres_password()
    app_db_password = generate_postgres_password()
    
    secrets_map = {
        'POSTGRES_PASSWORD': postgres_password,
        'APP_DB_PASSWORD': app_db_password,
        'JWT_SECRET': generate_jwt_secret(),
        'ENCRYPTION_KEY': generate_encryption_key(),
        'ENC_KEY_CURRENT': generate_encryption_key(),
        'BACKUP_PASSPHRASE': generate_passphrase(),
        'DEMO_PASSWORD_ADMIN': generate_demo_password(),
        'DEMO_PASSWORD_DOCTOR': generate_demo_password(),
        'DEMO_PASSWORD_ADMINISTRATIVO': generate_demo_password(),
        'DEMO_PASSWORD_AUDITOR': generate_demo_password(),
        'DEMO_PASSWORD_PACIENTE': generate_demo_password(),
    }
    
    # URLs de base de datos (se procesan por separado)
    database_url_password = app_db_password
    owner_database_url_password = postgres_password
    
    # Reemplazar valores falsos por secretos generados
    new_lines = []
    for line in lines:
        replaced = False
        for key, value in secrets_map.items():
            if line.startswith(f"{key}="):
                # Si el valor es un placeholder, reemplazarlo
                if "cambia-esto" in line or "cambia esto" in line.lower():
                    line = f"{key}={value}\n"
                    replaced = True
        # Caso especial: DATABASE_URL - reemplazar el password si es "cambia-esto"
        if not replaced and line.startswith("DATABASE_URL="):
            if "cambia-esto" in line:
                # URL: postgresql://user:password@host:port/db
                import re
                match = re.match(r'DATABASE_URL=(postgresql://[^:]+):[^@]+(@.+)', line.strip())
                if match:
                    line = f"DATABASE_URL={match.group(1)}:{database_url_password}{match.group(2)}\n"
        # Caso especial: OWNER_DATABASE_URL - reemplazar el password si es "cambia-esto"
        if not replaced and line.startswith("OWNER_DATABASE_URL="):
            if "cambia-esto" in line:
                # URL: postgresql://user:password@host:port/db
                import re
                match = re.match(r'OWNER_DATABASE_URL=(postgresql://[^:]+):[^@]+(@.+)', line.strip())
                if match:
                    line = f"OWNER_DATABASE_URL={match.group(1)}:{owner_database_url_password}{match.group(2)}\n"
        new_lines.append(line)
    
    # Escribir .env
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ .env generado a partir de .env.example")
    print(f"✅ Secretos generados aleatoriamente")
    print(f"⚠️  IMPORTANTE: Los secretos están en {env_file}")
    print(f"⚠️  NO los compartas ni los guardes en el repositorio.")

if __name__ == "__main__":
    if "--generate-env" in sys.argv:
        generate_env_from_example()
    else:
        print("=== Generación de Secretos para CriptoMed ===")
        print()
        print("Para generar un .env completo, usa:")
        print("  python scripts/generate_secrets.py --generate-env")
        print("  python scripts/generate_secrets.py --generate-env --force")
        print()
        print("Para imprimir secretos individuales (modo legado):")
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
