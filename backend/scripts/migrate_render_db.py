#!/usr/bin/env python3
"""
Script para migrar la base de datos de Render al nuevo modelo.

Este script:
1. Elimina todas las tablas existentes
2. Crea tablas con el nuevo modelo (incluyendo usuario_id en Paciente, detalle en AuditLog, etc.)
3. Carga los datos con el nuevo seed (3 doctores, paciente demo, pacientes distribuidos)

ADVERTENCIA: Esto eliminará todos los datos existentes en la base de datos.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from app.database import DATABASE_URL
from app.models import Base
from app.init_db import initialize_database

def migrate_database():
    """Migra la base de datos al nuevo modelo."""
    print("=== Migración de Base de Datos de Render ===")
    
    # Crear motor
    engine = create_engine(DATABASE_URL)
    
    try:
        # Eliminar todas las tablas existentes
        print("Eliminando tablas existentes...")
        Base.metadata.drop_all(bind=engine)
        print("Tablas eliminadas")
        
        # Crear tablas con el nuevo modelo
        print("Creando tablas con el nuevo modelo...")
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas con el nuevo modelo")
        
        # Ejecutar inicialización con el nuevo seed
        print("Ejecutando inicialización con el nuevo seed...")
        initialize_database()
        print("Inicialización completada")
        
        print("=== Migración completada exitosamente ===")
        print("Nuevas características:")
        print("- Rol 'paciente' agregado")
        print("- Campo 'usuario_id' en Paciente")
        print("- Campo 'detalle' en AuditLog")
        print("- Acción 'transferencia' en auditoría")
        print("- 3 doctores creados")
        print("- Pacientes distribuidos entre doctores")
        print("- Paciente demo creado y vinculado")
        
    except Exception as e:
        print(f"Error durante la migración: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    confirm = input("¿Estás seguro de que quieres eliminar todos los datos? (yes/no): ")
    if confirm.lower() == "yes":
        migrate_database()
    else:
        print("Migración cancelada")
