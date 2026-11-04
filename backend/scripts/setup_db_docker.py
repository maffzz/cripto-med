#!/usr/bin/env python3
"""
Script de configuración de base de datos para CriptoMed en Docker.
Crea todas las tablas a partir de los modelos de SQLAlchemy (app/models.py).
"""

import sys
import os
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def crear_tablas():
    print("=== Configuración de tablas para CriptoMed (Docker) ===")
    try:
        from app.database import engine, Base
        import app.models  # asegura que todos los modelos se registren en Base.metadata
        
        print("Creando tablas según modelos SQLAlchemy...")
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas exitosamente en PostgreSQL:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
        
        # Migraciones / extensiones idempotentes
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TYPE accionenum ADD VALUE IF NOT EXISTS 'login_fallido';
                ALTER TYPE accionenum ADD VALUE IF NOT EXISTS 'bloqueo';
                ALTER TYPE accionenum ADD VALUE IF NOT EXISTS 'exportacion';
                ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS intentos_fallidos INTEGER NOT NULL DEFAULT 0;
                ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS bloqueado_hasta TIMESTAMP;
            """))
            conn.commit()

        # Aplicar triggers y permisos sobre audit_logs
        aplicar_triggers_y_permisos(engine)
        return True
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        import traceback
        traceback.print_exc()
        return False

def aplicar_triggers_y_permisos(engine):
    print("\nAplicando triggers de inmutabilidad sobre audit_logs (NIST SP 800-92)...")
    sql_path = Path(__file__).resolve().parent / "sql" / "proteger_audit_logs.sql"
    if not sql_path.exists():
        sql_path = Path(__file__).resolve().parent.parent.parent / "scripts" / "sql" / "proteger_audit_logs.sql"

    if sql_path.exists():
        from sqlalchemy import text
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
        with engine.connect() as conn:
            conn.execute(text(sql_content))
            conn.commit()
        print("✅ Triggers y permisos de inmutabilidad aplicados exitosamente.")
    else:
        print(f"⚠️ Script SQL de protección no encontrado en {sql_path}")

def main():
    if not crear_tablas():
        sys.exit(1)
    print("\n=== Configuración de base de datos completada exitosamente ===")

if __name__ == "__main__":
    main()
