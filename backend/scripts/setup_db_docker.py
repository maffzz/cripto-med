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
        return True
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if not crear_tablas():
        sys.exit(1)
    print("\n=== Configuración de base de datos completada exitosamente ===")

if __name__ == "__main__":
    main()
