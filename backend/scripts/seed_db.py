#!/usr/bin/env python3
"""
Script de siembra de base de datos para CriptoMed.
Carga catálogos CIE-10, datos sintéticos de pacientes (Kaggle) con cifrado AES-256-GCM y usuarios demo.
No depende de pandas ni passlib para minimizar el peso del contenedor y garantizar reproducibilidad.
"""

import sys
import os
import csv
import uuid
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Usuario, Paciente, DiagnosticoCIE10, RolEnum
from app.crypto import encrypt, decrypt
from app.auth import get_password_hash, validate_password_policy


def buscar_archivo_datos(nombre: str) -> Path:
    """Busca un archivo de datos en varias rutas estándar del proyecto."""
    candidatos = [
        Path("/app/data") / nombre,
        Path(__file__).resolve().parent.parent.parent / "data" / nombre,
        Path("data") / nombre,
    ]
    for ruta in candidatos:
        if ruta.exists():
            return ruta
    return Path("/app/data") / nombre


def cargar_diagnosticos_cie10(db: Session) -> int:
    count = db.query(DiagnosticoCIE10).count()
    if count > 0:
        print(f"Diagnósticos CIE10 ya cargados ({count} registros), omitiendo...")
        return count

    ruta_csv = buscar_archivo_datos("cie10.csv")
    if not ruta_csv.exists():
        print(f"⚠️ Archivo no encontrado: {ruta_csv}")
        return 0

    print(f"Cargando CIE-10 desde {ruta_csv}...")
    contador = 0
    seen = set()

    with open(ruta_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            codigo = (row.get("codigo") or "").strip()
            if not codigo or codigo in seen:
                continue
            seen.add(codigo)
            descripcion = (row.get("diagnostico") or row.get("descripcion") or "").strip()
            diagnostico = DiagnosticoCIE10(codigo=codigo, descripcion=descripcion)
            db.add(diagnostico)
            contador += 1
            if contador % 1000 == 0:
                db.flush()

    db.commit()
    print(f"✅ Se cargaron {contador} diagnósticos CIE-10.")
    return contador


def cargar_pacientes(db: Session, limite: int = 500) -> int:
    count = db.query(Paciente).count()
    if count > 0:
        print(f"Pacientes ya cargados ({count} registros), omitiendo...")
        return count

    # Busca dataset mapeado con CIE-10 o estándar
    ruta_csv = buscar_archivo_datos("healthcare_dataset_mapped.csv")
    if not ruta_csv.exists():
        ruta_csv = buscar_archivo_datos("healthcare_dataset.csv")
    if not ruta_csv.exists():
        print(f"⚠️ Archivo de pacientes no encontrado en: {ruta_csv}")
        return 0

    print(f"Cargando y cifrando pacientes (AES-256-GCM) desde {ruta_csv}...")
    contador = 0

    with open(ruta_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader):
            if limite and contador >= limite:
                break

            paciente_id = uuid.uuid4()
            pid = str(paciente_id)
            nombre_limpio = str(row.get("Name", f"Paciente {index}")).title()

            # Cifrado en reposo con AAD según NIST SP 800-38D
            nombre_cifrado = encrypt(nombre_limpio, aad=f"pacientes.nombre.{pid}")
            diagnostico_cifrado = encrypt(str(row.get("Medical Condition", "")), aad=f"pacientes.diagnostico.{pid}")
            monto_cifrado = encrypt(str(row.get("Billing Amount", "0.0")), aad=f"pacientes.monto_facturado.{pid}")
            medicacion_cifrado = encrypt(str(row.get("Medication", "")), aad=f"pacientes.medicacion.{pid}")
            resultado_cifrado = encrypt(str(row.get("Test Results", "")), aad=f"pacientes.resultado_test.{pid}")

            codigo_cie10 = row.get("Codigo_CIE10")
            if codigo_cie10:
                cie_ref = db.query(DiagnosticoCIE10).filter(DiagnosticoCIE10.codigo == codigo_cie10).first()
                if not cie_ref:
                    codigo_cie10 = None

            fecha_admision_str = row.get("Date of Admission")
            try:
                fecha_admision = datetime.strptime(fecha_admision_str, "%Y-%m-%d") if fecha_admision_str else datetime.utcnow()
            except ValueError:
                fecha_admision = datetime.utcnow()

            fecha_alta = None
            if (index % 100) >= 40 and row.get("Discharge Date"):
                try:
                    fecha_alta = datetime.strptime(row.get("Discharge Date"), "%Y-%m-%d")
                except ValueError:
                    fecha_alta = None

            try:
                edad = int(row.get("Age", 30))
            except ValueError:
                edad = 30

            try:
                num_hab = int(row.get("Room Number", 101))
            except ValueError:
                num_hab = 101

            paciente = Paciente(
                id=paciente_id,
                nombre=nombre_cifrado,
                edad=edad,
                genero=row.get("Gender", "Otro"),
                tipo_sangre=row.get("Blood Type", "O+"),
                diagnostico=diagnostico_cifrado,
                codigo_cie10=codigo_cie10,
                fecha_admision=fecha_admision,
                doctor_id=None,
                hospital=row.get("Hospital", "Hospital Central"),
                proveedor_seguro=row.get("Insurance Provider", "Seguro General"),
                monto_facturado=monto_cifrado,
                numero_habitacion=str(num_hab),
                tipo_admision=row.get("Admission Type", "Urgencia"),
                fecha_alta=fecha_alta,
                medicacion=medicacion_cifrado,
                resultado_test=resultado_cifrado
            )
            db.add(paciente)
            contador += 1
            if contador % 100 == 0:
                db.flush()

    db.commit()
    print(f"✅ Se cargaron y cifraron {contador} pacientes.")
    return contador


def crear_usuarios_iniciales(db: Session) -> int:
    usuarios = [
        {
            "nombre": "Admin Sistema",
            "email": "admin@criptomed.com",
            "password": os.getenv("DEMO_PASSWORD_ADMIN", "CriptoMed_Adm#2026_Sec"),
            "rol": RolEnum.admin
        },
        {
            "nombre": "Dra. Ana Torres",
            "email": "doctor@criptomed.com",
            "password": os.getenv("DEMO_PASSWORD_DOCTOR", "Medicos_CriptoMed#2026!"),
            "rol": RolEnum.doctor
        },
        {
            "nombre": "Dr. Luis Ramírez",
            "email": "dr.ramirez@criptomed.com",
            "password": os.getenv("DEMO_PASSWORD_DOCTOR", "Medicos_CriptoMed#2026!"),
            "rol": RolEnum.doctor
        },
        {
            "nombre": "Dra. Carla Quispe",
            "email": "dra.quispe@criptomed.com",
            "password": os.getenv("DEMO_PASSWORD_DOCTOR", "Medicos_CriptoMed#2026!"),
            "rol": RolEnum.doctor
        },
        {
            "nombre": "Maria Lopez",
            "email": "admin@clinica.com",
            "password": os.getenv("DEMO_PASSWORD_ADMINISTRATIVO", "Gestion_Clinica#2026!"),
            "rol": RolEnum.administrativo
        },
        {
            "nombre": "Auditor Externo",
            "email": "auditor@criptomed.com",
            "password": os.getenv("DEMO_PASSWORD_AUDITOR", "Control_Forense#2026!"),
            "rol": RolEnum.auditor
        },
        {
            "nombre": "Paciente Demo",
            "email": "paciente@criptomed.com",
            "password": os.getenv("DEMO_PASSWORD_PACIENTE", "Salud_Titular#2026_Clave!"),
            "rol": RolEnum.paciente
        }
    ]

    contador = 0
    for udata in usuarios:
        existe = db.query(Usuario).filter(Usuario.email == udata["email"]).first()
        pwd = udata["password"] # clave desde DEMO_PASSWORD_* del .env
        validate_password_policy(pwd, email=udata["email"], nombre=udata["nombre"])
        if existe:
            existe.nombre = udata["nombre"] # alinea nombre de demo
            existe.password_hash = get_password_hash(pwd) # rehash para coincidir con el .env actual
            existe.intentos_fallidos = 0 # desbloquea tras pruebas fallidas
            existe.bloqueado_hasta = None # limpia ventana de bloqueo
            existe.activo = True # asegura que el usuario de demo pueda entrar
            existe.rol = udata["rol"] # mantiene el rol esperado
            db.commit()
            continue

        
        usuario = Usuario(
            nombre=udata["nombre"],
            email=udata["email"],
            password_hash=get_password_hash(pwd),
            rol=udata["rol"],
            activo=True
        )
        db.add(usuario)
        contador += 1

    db.commit()
    print(f"✅ Se sincronizaron/crearon {contador} usuarios de demo.")

    # Vincular o crear expediente médico para el Paciente Demo
    paciente_user = db.query(Usuario).filter(Usuario.email == "paciente@criptomed.com").first()
    dra_torres = db.query(Usuario).filter(Usuario.email == "doctor@criptomed.com").first()
    dr_ramirez = db.query(Usuario).filter(Usuario.email == "dr.ramirez@criptomed.com").first()
    dra_quispe = db.query(Usuario).filter(Usuario.email == "dra.quispe@criptomed.com").first()

    if paciente_user:
        expediente_demo = db.query(Paciente).filter(Paciente.usuario_id == paciente_user.id).first()
        if not expediente_demo:
            nuevo_pid = uuid.uuid4()
            pid_str = str(nuevo_pid)
            consent_fecha = datetime.utcnow() - timedelta(days=10)
            expediente_demo = Paciente(
                id=nuevo_pid,
                usuario_id=paciente_user.id,
                doctor_id=dra_torres.id if dra_torres else None,
                nombre=encrypt("Paciente Demo", aad=f"pacientes.nombre.{pid_str}"),
                edad=34,
                genero="Femenino",
                tipo_sangre="O+",
                diagnostico=encrypt("Hipertensión esencial", aad=f"pacientes.diagnostico.{pid_str}"),
                codigo_cie10="I10",
                fecha_admision=datetime.utcnow() - timedelta(days=15),
                hospital="Clínica San Borja",
                proveedor_seguro="Rímac Seguros",
                monto_facturado=encrypt("450.00", aad=f"pacientes.monto_facturado.{pid_str}"),
                numero_habitacion="302",
                tipo_admision="Consulta Externa",
                fecha_alta=None,
                medicacion=encrypt("Losartán 50mg cada 12 horas", aad=f"pacientes.medicacion.{pid_str}"),
                resultado_test=encrypt("Presión arterial: 120/80 mmHg. Perfil lipídico normal.", aad=f"pacientes.resultado_test.{pid_str}"),
                consentimiento_fecha=consent_fecha,
                consentimiento_version="v1.0"
            )
            db.add(expediente_demo)
            db.commit()
            print(f"✅ Expediente médico creado para Paciente Demo (asignado a Dra. Ana Torres).")
        else:
            # Asegurar que tenga consentimiento y asignación
            if not expediente_demo.consentimiento_fecha:
                expediente_demo.consentimiento_fecha = datetime.utcnow() - timedelta(days=10)
                expediente_demo.consentimiento_version = "v1.0"
            if not expediente_demo.doctor_id and dra_torres:
                expediente_demo.doctor_id = dra_torres.id
            db.commit()

    # Asignar doctores a pacientes existentes que no tengan doctor_id
    if dra_torres and dr_ramirez and dra_quispe:
        pacientes_sin_doc = db.query(Paciente).filter(Paciente.doctor_id == None, Paciente.usuario_id == None).all()
        for idx, p in enumerate(pacientes_sin_doc):
            if idx % 3 == 0:
                p.doctor_id = dra_torres.id
            elif idx % 3 == 1:
                p.doctor_id = dr_ramirez.id
            else:
                p.doctor_id = dra_quispe.id
            if not p.consentimiento_fecha:
                p.consentimiento_fecha = datetime.utcnow() - timedelta(days=30)
                p.consentimiento_version = "v1.0"
        db.commit()
        if pacientes_sin_doc:
            print(f"✅ Asignados {len(pacientes_sin_doc)} pacientes a los 3 doctores equitativamente.")

    return contador


def verificar_datos(db: Session) -> None:
    print("\n--- Verificación de Datos Sembrados ---")
    print(f"Usuarios en BD: {db.query(Usuario).count()}")
    print(f"Pacientes en BD: {db.query(Paciente).count()}")
    print(f"Diagnósticos CIE-10 en BD: {db.query(DiagnosticoCIE10).count()}")

    paciente = db.query(Paciente).first()
    if paciente:
        pid = str(paciente.id)
        print(f"\nEjemplo de paciente:")
        print(f"  ID: {pid}")
        print(f"  Nombre (cifrado en reposo): {paciente.nombre[:55]}...")
        print(f"  Nombre (descifrado con AAD): {decrypt(paciente.nombre, aad=f'pacientes.nombre.{pid}')}")
        print(f"  Diagnóstico (cifrado): {paciente.diagnostico[:55]}...")
        print(f"  Diagnóstico (descifrado): {decrypt(paciente.diagnostico, aad=f'pacientes.diagnostico.{pid}')}")
        print(f"  Edad: {paciente.edad} | Género: {paciente.genero}")


def main():
    print("=== CriptoMed: Carga y Cifrado de Datos Sintéticos ===")
    enc_keys = os.getenv("ENC_KEYS", "")
    current_kid = os.getenv("ENC_KEY_CURRENT", "")
    print(f"Cifrado configurado: {len(enc_keys.split(',')) if enc_keys else 0} llaves en anillo, llave activa: '{current_kid}'")

    db = SessionLocal()
    try:
        cargar_diagnosticos_cie10(db)
        cargar_pacientes(db)
        crear_usuarios_iniciales(db)
        verificar_datos(db)
        print("\n=== Carga de datos completada exitosamente ===")
    except Exception as e:
        print(f"❌ Error durante la carga de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
