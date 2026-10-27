#!/usr/bin/env python3

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from passlib.context import CryptContext
from sqlalchemy import text

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import AuditLog, Usuario, Paciente, DiagnosticoCIE10, RolEnum
from app.crypto import encrypt, decrypt
from app.config import ROOT_DIR

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def cargar_diagnosticos_cie10(db: Session) -> int:
    # Verificar si ya hay datos (idempotente)
    count = db.query(DiagnosticoCIE10).count()
    if count > 0:
        print(f"Diagnosticos CIE10 ya cargados ({count} registros), omitiendo...")
        return count

    ruta_csv = ROOT_DIR / "data" / "cie10.csv"
    if not ruta_csv.exists():
        print(f"error: archivo no encontrado: {ruta_csv}")
        return 0
    
    df = pd.read_csv(ruta_csv)
    df = df.drop_duplicates(subset=["codigo"])
    contador = 0
    
    for _, row in df.iterrows():
        codigo = row["codigo"]
        descripcion = row["diagnostico"]
        
        diagnostico = DiagnosticoCIE10(codigo=codigo, descripcion=descripcion)
        db.add(diagnostico)
        contador += 1
    
    db.commit()
    print(f"se cargaron {contador} diagnosticos cie10")
    return contador


def cargar_pacientes(db: Session) -> int:
    # Verificar si ya hay datos (idempotente)
    count = db.query(Paciente).count()
    if count > 0:
        print(f"Pacientes ya cargados ({count} registros), omitiendo...")
        return count
    
    ruta_csv = ROOT_DIR / "data" / "healthcare_dataset_mapped.csv"
    if not ruta_csv.exists():
        print(f"error: archivo no encontrado: {ruta_csv}")
        return 0
    
    df = pd.read_csv(ruta_csv)
    contador = 0
    
    mapeo = {
        "Name": "nombre",
        "Age": "edad",
        "Gender": "genero",
        "Blood Type": "tipo_sangre",
        "Medical Condition": "diagnostico",
        "Date of Admission": "fecha_admision",
        "Doctor": "doctor_id",
        "Hospital": "hospital",
        "Insurance Provider": "proveedor_seguro",
        "Billing Amount": "monto_facturado",
        "Room Number": "numero_habitacion",
        "Admission Type": "tipo_admision",
        "Discharge Date": "fecha_alta",
        "Medication": "medicacion",
        "Test Results": "resultado_test",
        "Codigo_CIE10": "codigo_cie10"
    }
    
    for index, row in df.iterrows():
        nombre_limpio = str(row["Name"]).title()
        
        nombre_cifrado = encrypt(nombre_limpio)
        diagnostico_cifrado = encrypt(str(row["Medical Condition"]))
        monto_cifrado = encrypt(str(row["Billing Amount"]))
        medicacion_cifrado = encrypt(str(row["Medication"]))
        resultado_cifrado = encrypt(str(row["Test Results"]))
        
        codigo_cie10 = row["Codigo_CIE10"]
        diagnostico_ref = db.query(DiagnosticoCIE10).filter(DiagnosticoCIE10.codigo == codigo_cie10).first()
        if not diagnostico_ref:
            codigo_cie10 = None
        
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
        db.add(paciente)
        contador += 1
    
    db.commit()
    print(f"se cargaron {contador} pacientes")
    return contador


def crear_usuarios_iniciales(db: Session) -> int:
    # Verificar si ya hay datos (idempotente)
    count = db.query(Usuario).count()
    if count > 0:
        print(f"Usuarios ya creados ({count} registros), omitiendo...")
        return count
    
    # Leer contraseñas de variables de entorno
    usuarios = [
        {
            "nombre": "Admin Sistema",
            "email": "admin@criptomed.com",
            "password": os.getenv("DEMO_PASSWORD_ADMIN", "admin123"),
            "rol": RolEnum.admin
        },
        {
            "nombre": "Dr. Juan Perez",
            "email": "doctor@criptomed.com",
            "password": os.getenv("DEMO_PASSWORD_DOCTOR", "doctor123"),
            "rol": RolEnum.doctor
        },
        {
            "nombre": "Maria Lopez",
            "email": "admin@clinica.com",
            "password": os.getenv("DEMO_PASSWORD_ADMINISTRATIVO", "admin123"),
            "rol": RolEnum.administrativo
        },
        {
            "nombre": "Auditor Externo",
            "email": "auditor@criptomed.com",
            "password": os.getenv("DEMO_PASSWORD_AUDITOR", "auditor123"),
            "rol": RolEnum.auditor
        }
    ]
    
    contador = 0
    
    for usuario_data in usuarios:
        existe = db.query(Usuario).filter(Usuario.email == usuario_data["email"]).first()
        if existe:
            continue
        
        usuario = Usuario(
            nombre=usuario_data["nombre"],
            email=usuario_data["email"],
            password_hash=hash_password(usuario_data["password"]),
            rol=usuario_data["rol"],
            activo=True
        )
        db.add(usuario)
        contador += 1
    
    db.commit()
    print(f"se crearon {contador} usuarios iniciales")
    return contador


def verificar_datos(db: Session) -> None:
    print("\n--- verificacion de datos ---")
    
    count_usuarios = db.query(Usuario).count()
    print(f"usuarios en bd: {count_usuarios}")
    
    count_pacientes = db.query(Paciente).count()
    print(f"pacientes en bd: {count_pacientes}")
    
    count_diagnosticos = db.query(DiagnosticoCIE10).count()
    print(f"diagnosticos cie10 en bd: {count_diagnosticos}")
    
    paciente = db.query(Paciente).first()
    if paciente:
        print(f"\nejemplo de paciente:")
        print(f"  nombre (cifrado): {paciente.nombre[:50]}...")
        print(f"  nombre (descifrado): {decrypt(paciente.nombre)[:50]}...")
        print(f"  edad: {paciente.edad}")
        print(f"  genero: {paciente.genero}")


def main():
    print("=== script de carga de datos para criptomed ===")
    print("este script cargara los datos de ejemplo en la base de datos\n")
    
    # Leer ENC_KEYS y ENC_KEY_CURRENT (para compatibilidad futura)
    enc_keys = os.getenv("ENC_KEYS", "1")
    enc_key_current = os.getenv("ENC_KEY_CURRENT")
    print(f"Configuracion de cifrado: {enc_keys} llaves, llave actual: {'configurada' if enc_key_current else 'no configurada'}")
    
    db = SessionLocal()
    
    try:
        print("--- paso 1: cargar diagnosticos cie10 ---")
        cargar_diagnosticos_cie10(db)
        
        print("\n--- paso 2: cargar pacientes ---")
        cargar_pacientes(db)
        
        print("\n--- paso 3: crear usuarios iniciales ---")
        crear_usuarios_iniciales(db)
        
        verificar_datos(db)
        
        print("\n=== carga de datos completada exitosamente ===")
        
    except Exception as e:
        print(f"error durante la carga de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
