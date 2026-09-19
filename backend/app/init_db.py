"""
Script de inicialización automática de la base de datos
Se ejecuta al inicio del servicio para verificar si las tablas existen
y crearlas si no existen.
"""

import os
from sqlalchemy import inspect
from app.database import engine, Base
from app.models import Usuario, Paciente, DiagnosticoCIE10
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

def check_and_create_tables():
    """Verifica si las tablas existen y las crea si no"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    required_tables = ['usuarios', 'pacientes', 'diagnosticos_cie10', 'audit_logs']
    
    # Verificar si todas las tablas existen
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        print(f"Tablas faltantes: {missing_tables}")
        print("Creando tablas...")
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas exitosamente")
        return True
    else:
        print("Todas las tablas ya existen")
        return False

def check_and_create_users():
    """Verifica si hay usuarios y crea los iniciales si no existen"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        user_count = session.query(Usuario).count()
        
        if user_count == 0:
            print("No hay usuarios, creando usuarios iniciales...")
            
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            usuarios_iniciales = [
                {
                    "email": "admin@criptomed.com",
                    "nombre": "Admin Sistema",
                    "rol": "admin",
                    "password": "admin123"
                },
                {
                    "email": "doctor@criptomed.com",
                    "nombre": "Doctor Principal",
                    "rol": "doctor",
                    "password": "doctor123"
                },
                {
                    "email": "admin@clinica.com",
                    "nombre": "Maria Lopez",
                    "rol": "administrativo",
                    "password": "admin123"
                },
                {
                    "email": "auditor@criptomed.com",
                    "nombre": "Auditor Externo",
                    "rol": "auditor",
                    "password": "auditor123"
                }
            ]
            
            from app.models import RolEnum
            
            for usuario_data in usuarios_iniciales:
                usuario = Usuario(
                    email=usuario_data["email"],
                    nombre=usuario_data["nombre"],
                    rol=RolEnum(usuario_data["rol"]),
                    password_hash=pwd_context.hash(usuario_data["password"])
                )
                session.add(usuario)
            
            session.commit()
            print(f"Se crearon {len(usuarios_iniciales)} usuarios iniciales")
            return True
        else:
            print(f"Ya existen {user_count} usuarios")
            return False
    except Exception as e:
        print(f"Error al crear usuarios: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def initialize_database():
    """Función principal de inicialización"""
    print("=== Inicialización de base de datos ===")
    
    # Crear tablas si no existen
    tables_created = check_and_create_tables()
    
    # Crear usuarios si no existen
    users_created = check_and_create_users()
    
    if tables_created or users_created:
        print("=== Inicialización completada ===")
    else:
        print("=== Base de datos ya inicializada ===")
    
    return True

if __name__ == "__main__":
    initialize_database()
