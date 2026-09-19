#!/usr/bin/env python3
"""
Script de configuración de tablas para CriptoMed en Render (sin Docker)
Este script crea las tablas en PostgreSQL usando la DATABASE_URL de Render
"""

import os
import sys
from pathlib import Path

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from app.models import Base

def setup_database():
    """Crea todas las tablas en la base de datos de Render"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL no está configurada")
        return False
    
    # Crear engine con SSL requerido por Render
    engine = create_engine(database_url, pool_pre_ping=True)
    
    try:
        print("=== Configuración de tablas para CriptoMed (Render) ===")
        print("DATABASE_URL:", database_url[:50] + "..." if len(database_url) > 50 else database_url)
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        print("\n=== Tablas creadas exitosamente ===")
        print("  - usuarios")
        print("  - pacientes")
        print("  - diagnosticos_cie10")
        print("  - audit_logs")
        
        print("\n=== Configuración completada exitosamente ===")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
