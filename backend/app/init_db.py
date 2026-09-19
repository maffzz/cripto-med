"""
Script de inicialización automática de la base de datos
Se ejecuta al inicio del servicio para verificar si las tablas existen
y crearlas si no existen.
"""

import os
import pandas as pd
from pathlib import Path
from sqlalchemy import inspect
from app.database import engine, Base
from app.models import Usuario, Paciente, DiagnosticoCIE10, RolEnum
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from app.crypto import encrypt

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

def check_and_load_diagnosticos():
    """Verifica si hay diagnósticos CIE-10 y carga los datos si no existen"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        diagnostico_count = session.query(DiagnosticoCIE10).count()
        
        if diagnostico_count == 0:
            print("No hay diagnósticos CIE-10, cargando datos...")
            
            ruta_cie10 = Path(__file__).parent.parent.parent / "data" / "cie10.csv"
            
            if not ruta_cie10.exists():
                print(f"WARNING: Archivo CIE-10 no encontrado: {ruta_cie10}")
                print("No se cargarán diagnósticos CIE-10 automáticamente")
                return False
            
            df_cie10 = pd.read_csv(ruta_cie10)
            contador_cie10 = 0
            
            for _, row in df_cie10.iterrows():
                diagnostico = DiagnosticoCIE10(
                    codigo=row["code"],
                    descripcion=row["description"]
                )
                session.add(diagnostico)
                contador_cie10 += 1
            
            session.commit()
            print(f"Se cargaron {contador_cie10} diagnósticos CIE-10")
            return True
        else:
            print(f"Ya existen {diagnostico_count} diagnósticos CIE-10")
            return False
    except Exception as e:
        print(f"Error al cargar diagnósticos CIE-10: {e}")
        session.rollback()
        return False
    finally:
        session.close()

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
                    "password": "admin123"  # password corto (< 72 bytes)
                },
                {
                    "email": "doctor@criptomed.com",
                    "nombre": "Doctor Principal",
                    "rol": "doctor",
                    "password": "doctor123"  # password corto (< 72 bytes)
                },
                {
                    "email": "admin@clinica.com",
                    "nombre": "Maria Lopez",
                    "rol": "administrativo",
                    "password": "admin123"  # password corto (< 72 bytes)
                },
                {
                    "email": "auditor@criptomed.com",
                    "nombre": "Auditor Externo",
                    "rol": "auditor",
                    "password": "auditor123"  # password corto (< 72 bytes)
                }
            ]
            
            from app.models import RolEnum
            
            for usuario_data in usuarios_iniciales:
                # Los passwords ya son cortos, no necesitan truncación
                password = usuario_data["password"]
                print(f"Creando usuario: {usuario_data['email']}, password length: {len(password)}")
                
                usuario = Usuario(
                    email=usuario_data["email"],
                    nombre=usuario_data["nombre"],
                    rol=RolEnum(usuario_data["rol"]),
                    password_hash=pwd_context.hash(password)
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

def check_and_load_pacientes():
    """Verifica si hay pacientes y carga los datos si no existen"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        paciente_count = session.query(Paciente).count()
        
        if paciente_count == 0:
            print("No hay pacientes, cargando datos del dataset...")
            
            # Ruta al CSV en el repositorio
            ruta_pacientes = Path(__file__).parent.parent.parent / "data" / "healthcare_dataset.csv"
            
            if not ruta_pacientes.exists():
                print(f"WARNING: Archivo de pacientes no encontrado: {ruta_pacientes}")
                print("No se cargarán pacientes automáticamente")
                return False
            
            df_pacientes = pd.read_csv(ruta_pacientes)
            contador_pacientes = 0
            
            print(f"Cargando {len(df_pacientes)} pacientes del dataset...")
            
            for index, row in df_pacientes.iterrows():
                # Limpia el nombre: title case
                nombre_limpio = str(row["Name"]).title()
                
                # Campos sensibles cifrados
                nombre_cifrado = encrypt(nombre_limpio)
                diagnostico_cifrado = encrypt(str(row["Medical Condition"]))
                monto_cifrado = encrypt(str(row["Billing Amount"]))
                medicacion_cifrado = encrypt(str(row["Medication"]))
                resultado_cifrado = encrypt(str(row["Test Results"]))
                
                # Verifica si el código CIE-10 existe
                codigo_cie10 = row["Codigo_CIE10"]
                diagnostico_ref = session.query(DiagnosticoCIE10).filter(
                    DiagnosticoCIE10.codigo == codigo_cie10
                ).first()
                if not diagnostico_ref:
                    codigo_cie10 = None
                
                # 40% de pacientes activos
                fecha_alta = row["Discharge Date"] if (index % 100) >= 40 else None
                
                paciente = Paciente(
                    nombre=nombre_cifrado,
                    edad=int(row["Age"]),
                    genero=row["Gender"],
                    tipo_sangre=row["Blood Type"],
                    diagnostico=diagnostico_cifrado,
                    codigo_cie10=codigo_cie10,
                    fecha_admision=row["Date of Admission"],
                    doctor_id=None,
                    hospital=row["Hospital"],
                    proveedor_seguro=row["Insurance Provider"],
                    monto_facturado=monto_cifrado,
                    numero_habitacion=int(row["Room Number"]),
                    tipo_admision=row["Admission Type"],
                    fecha_alta=fecha_alta,
                    medicacion=medicacion_cifrado,
                    resultado_test=resultado_cifrado
                )
                session.add(paciente)
                contador_pacientes += 1
                
                # Commit cada 1000 pacientes para no saturar memoria
                if contador_pacientes % 1000 == 0:
                    session.commit()
                    print(f"Progreso: {contador_pacientes}/{len(df_pacientes)} pacientes cargados")
            
            session.commit()
            print(f"Se cargaron {contador_pacientes} pacientes")
            return True
        else:
            print(f"Ya existen {paciente_count} pacientes")
            return False
    except Exception as e:
        print(f"Error al cargar pacientes: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def initialize_database():
    """Función principal de inicialización"""
    print("=== Inicialización de base de datos ===")
    
    # Crear tablas si no existen
    tables_created = check_and_create_tables()
    
    # Cargar diagnósticos CIE-10 si no existen
    diagnosticos_loaded = check_and_load_diagnosticos()
    
    # Crear usuarios si no existen
    users_created = check_and_create_users()
    
    # Cargar pacientes si no existen
    pacientes_loaded = check_and_load_pacientes()
    
    if tables_created or diagnosticos_loaded or users_created or pacientes_loaded:
        print("=== Inicialización completada ===")
    else:
        print("=== Base de datos ya inicializada ===")
    
    return True

if __name__ == "__main__":
    initialize_database()
