#!/usr/bin/env python3
"""
Script de carga de datos para CriptoMed en Render (sin Docker)
Este script carga los datos de ejemplo en la base de datos de Render
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Usuario, Paciente, DiagnosticoCIE10, RolEnum
from app.crypto import encrypt

def seed_database():
    """Carga los datos de ejemplo en la base de datos de Render"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL no está configurada")
        return False
    
    # Crear engine con SSL requerido por Render
    engine = create_engine(database_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=== Carga de datos para CriptoMed (Render) ===")
        
        # --- Paso 1: Cargar diagnósticos CIE-10 ---
        print("\n--- Paso 1: Cargar diagnósticos CIE-10 ---")
        ruta_cie10 = Path(__file__).parent.parent.parent / "data" / "cie10.csv"
        
        if not ruta_cie10.exists():
            print(f"WARNING: Archivo CIE-10 no encontrado: {ruta_cie10}")
            print("Saltando carga de diagnósticos CIE-10")
        else:
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
        
        # --- Paso 2: Cargar pacientes ---
        print("\n--- Paso 2: Cargar pacientes ---")
        ruta_pacientes = Path(__file__).parent.parent.parent / "data" / "healthcare_dataset.csv"
        
        if not ruta_pacientes.exists():
            print(f"ERROR: Archivo de pacientes no encontrado: {ruta_pacientes}")
            return False
        
        df_pacientes = pd.read_csv(ruta_pacientes)
        contador_pacientes = 0
        
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
        
        session.commit()
        print(f"Se cargaron {contador_pacientes} pacientes")
        
        # --- Paso 3: Crear usuarios iniciales ---
        print("\n--- Paso 3: Crear usuarios iniciales ---")
        
        usuarios_iniciales = [
            {
                "email": "admin@criptomed.com",
                "nombre": "Admin Sistema",
                "rol": RolEnum.admin,
                "password": "admin123"
            },
            {
                "email": "doctor@criptomed.com",
                "nombre": "Doctor Principal",
                "rol": RolEnum.doctor,
                "password": "doctor123"
            },
            {
                "email": "admin@clinica.com",
                "nombre": "Maria Lopez",
                "rol": RolEnum.administrativo,
                "password": "admin123"
            },
            {
                "email": "auditor@criptomed.com",
                "nombre": "Auditor Externo",
                "rol": RolEnum.auditor,
                "password": "auditor123"
            }
        ]
        
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        for usuario_data in usuarios_iniciales:
            usuario = Usuario(
                email=usuario_data["email"],
                nombre=usuario_data["nombre"],
                rol=usuario_data["rol"],
                password_hash=pwd_context.hash(usuario_data["password"])
            )
            session.add(usuario)
        
        session.commit()
        print(f"Se crearon {len(usuarios_iniciales)} usuarios iniciales")
        
        # --- Verificación ---
        print("\n--- Verificación de datos ---")
        print(f"Usuarios en BD: {session.query(Usuario).count()}")
        print(f"Pacientes en BD: {session.query(Paciente).count()}")
        print(f"Diagnósticos CIE-10 en BD: {session.query(DiagnosticoCIE10).count()}")
        
        print("\n=== Carga de datos completada exitosamente ===")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        session.rollback()
        return False
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
