#!/usr/bin/env python3

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import bcrypt
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Usuario, Paciente, DiagnosticoCIE10, RolEnum
from app.crypto import encrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def cargar_usuarios_demo(db: Session) -> int:
    """Carga usuarios de demo (idempotente)"""
    count = db.query(Usuario).count()
    if count > 0:
        print(f"Usuarios ya cargados ({count} registros), omitiendo...")
        return count
    
    usuarios = [
        {
            "username": "admin",
            "password": os.getenv("DEMO_PASSWORD_ADMIN", "admin123"),
            "rol": RolEnum.ADMIN,
            "email": "admin@criptomed.local"
        },
        {
            "username": "doctor1",
            "password": os.getenv("DEMO_PASSWORD_DOCTOR", "doctor123"),
            "rol": RolEnum.DOCTOR,
            "email": "doctor1@criptomed.local"
        },
        {
            "username": "admin1",
            "password": os.getenv("DEMO_PASSWORD_ADMINISTRATIVO", "admin123"),
            "rol": RolEnum.ADMINISTRATIVO,
            "email": "admin1@criptomed.local"
        },
        {
            "username": "auditor1",
            "password": os.getenv("DEMO_PASSWORD_AUDITOR", "auditor123"),
            "rol": RolEnum.AUDITOR,
            "email": "auditor1@criptomed.local"
        },
        {
            "username": "paciente1",
            "password": os.getenv("DEMO_PASSWORD_PACIENTE", "paciente123"),
            "rol": RolEnum.PACIENTE,
            "email": "paciente1@criptomed.local"
        }
    ]
    
    contador = 0
    for u in usuarios:
        password_hash = hash_password(u["password"])
        usuario = Usuario(
            username=u["username"],
            password_hash=password_hash,
            rol=u["rol"],
            email=u["email"]
        )
        db.add(usuario)
        contador += 1
    
    db.commit()
    print(f"Usuarios demo creados: {contador}")
    return contador

def cargar_pacientes_demo(db: Session) -> int:
    """Carga pacientes de demo (idempotente)"""
    count = db.query(Paciente).count()
    if count > 0:
        print(f"Pacientes ya cargados ({count} registros), omitiendo...")
        return count
    
    # Obtener doctor1
    doctor = db.query(Usuario).filter(Usuario.username == "doctor1").first()
    if not doctor:
        print("Error: doctor1 no encontrado")
        return 0
    
    pacientes = [
        {
            "nombre": "Juan",
            "apellido": "Perez",
            "fecha_nacimiento": "1980-01-15",
            "dni": "12345678",
            "doctor_id": doctor.id,
            "diagnostico": "Diabetes tipo 2",
            "medicacion": "Metformina 500mg",
            "resultado_test": "Glucosa 180 mg/dL"
        },
        {
            "nombre": "Maria",
            "apellido": "Garcia",
            "fecha_nacimiento": "1975-05-20",
            "dni": "87654321",
            "doctor_id": doctor.id,
            "diagnostico": "Hipertension arterial",
            "medicacion": "Losartan 50mg",
            "resultado_test": "Presion 140/90 mmHg"
        }
    ]
    
    contador = 0
    for p in pacientes:
        # Encriptar campos sensibles
        diagnostico_enc = encrypt(p["diagnostico"]) if p["diagnostico"] else None
        medicacion_enc = encrypt(p["medicacion"]) if p["medicacion"] else None
        resultado_enc = encrypt(p["resultado_test"]) if p["resultado_test"] else None
        
        paciente = Paciente(
            nombre=p["nombre"],
            apellido=p["apellido"],
            fecha_nacimiento=p["fecha_nacimiento"],
            dni=p["dni"],
            doctor_id=p["doctor_id"],
            diagnostico=diagnostico_enc,
            medicacion=medicacion_enc,
            resultado_test=resultado_enc
        )
        db.add(paciente)
        contador += 1
    
    db.commit()
    print(f"Pacientes demo creados: {contador}")
    return contador

def cargar_diagnosticos_cie10(db: Session) -> int:
    """Carga algunos diagnosticos CIE10 de ejemplo (idempotente)"""
    count = db.query(DiagnosticoCIE10).count()
    if count > 0:
        print(f"Diagnosticos CIE10 ya cargados ({count} registros), omitiendo...")
        return count
    
    diagnosticos = [
        {"codigo": "E11", "descripcion": "Diabetes mellitus tipo 2"},
        {"codigo": "I10", "descripcion": "Hipertension esencial (primaria)"},
        {"codigo": "J00", "descripcion": "Rinofaringitis aguda (resfriado comun)"},
        {"codigo": "U07.1", "descripcion": "COVID-19, virus identificado"}
    ]
    
    contador = 0
    for d in diagnosticos:
        diagnostico = DiagnosticoCIE10(codigo=d["codigo"], descripcion=d["descripcion"])
        db.add(diagnostico)
        contador += 1
    
    db.commit()
    print(f"Diagnosticos CIE10 creados: {contador}")
    return contador

def main():
    print("=== Script de seed simplificado para CriptoMed ===")
    
    db = SessionLocal()
    try:
        cargar_usuarios_demo(db)
        cargar_pacientes_demo(db)
        cargar_diagnosticos_cie10(db)
        print("\n=== Seed completado exitosamente ===")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
