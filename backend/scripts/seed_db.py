#!/usr/bin/env python3 # shebang para python3

import sys # para manipular path
from pathlib import Path # para rutas de archivos

# agrega el directorio backend al path para poder importar app
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd # para leer csvs
from passlib.context import CryptContext # para hashear contraseñas
from sqlalchemy import text # para ejecutar sentencias SQL 

from sqlalchemy.orm import Session # para sesiones de base de datos
from app.database import SessionLocal # para crear sesiones de base de datos
from app.models import AuditLog, Usuario, Paciente, DiagnosticoCIE10, RolEnum # modelos de la base de datos
from app.crypto import encrypt, decrypt # para cifrar y descifrar campos sensibles
from app.config import ROOT_DIR # directorio raiz del proyecto

# contexto de hasheo de contraseñas con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # usa bcrypt


def hash_password(password: str) -> str: # hashea una contraseña
    return pwd_context.hash(password) # retorna el hash


def cargar_diagnosticos_cie10(db: Session) -> int: # carga diagnosticos desde csv

    # Limpieza previa respetando relaciones de clave foránea mediante SQL directo
    db.execute(text("DELETE FROM pacientes;"))
    db.execute(text("DELETE FROM diagnosticos_cie10;"))
    db.commit()

    ruta_csv = ROOT_DIR / "data" / "cie10.csv" # ruta al archivo csv
    if not ruta_csv.exists(): # verifica que exista
        print(f"error: archivo no encontrado: {ruta_csv}")
        return 0
    
    
    df = pd.read_csv(ruta_csv) # lee el csv
    df = df.drop_duplicates(subset=["codigo"]) # elimina duplicados por codigo
    contador = 0 # contador de registros insertados
    
    for _, row in df.iterrows(): # itera sobre cada fila
        codigo = row["codigo"] # codigo del diagnostico
        descripcion = row["diagnostico"] # descripcion del diagnostico
        
        # crea el registro
        diagnostico = DiagnosticoCIE10(codigo=codigo, descripcion=descripcion)
        db.add(diagnostico) # agrega a la sesion
        contador += 1 # incrementa contador
    
    db.commit() # confirma los cambios
    print(f"se cargaron {contador} diagnosticos cie10")
    return contador


def cargar_pacientes(db: Session) -> int: # carga pacientes desde csv
    ruta_csv = ROOT_DIR / "data" / "healthcare_dataset_mapped.csv" # ruta al archivo csv
    if not ruta_csv.exists(): # verifica que exista
        print(f"error: archivo no encontrado: {ruta_csv}")
        return 0
    
    # limpia la tabla primero
    db.execute(text("DELETE FROM pacientes;"))
    db.commit()
    
    df = pd.read_csv(ruta_csv) # lee el csv
    contador = 0 # contador de registros insertados
    
    # mapeo de columnas del csv a los campos del modelo
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
    
    for index, row in df.iterrows(): # itera sobre cada fila
        # limpia el nombre: title case (solo primeras letras mayusculas)
        nombre_limpio = str(row["Name"]).title() # convierte a title case
        
        # campos sensibles que deben cifrarse
        nombre_cifrado = encrypt(nombre_limpio) # cifra el nombre limpio
        diagnostico_cifrado = encrypt(str(row["Medical Condition"])) # cifra el diagnostico
        monto_cifrado = encrypt(str(row["Billing Amount"])) # cifra el monto
        medicacion_cifrado = encrypt(str(row["Medication"])) # cifra la medicacion
        resultado_cifrado = encrypt(str(row["Test Results"])) # cifra el resultado
        
        # verifica si el codigo cie10 existe
        codigo_cie10 = row["Codigo_CIE10"]
        diagnostico_ref = db.query(DiagnosticoCIE10).filter(DiagnosticoCIE10.codigo == codigo_cie10).first()
        if not diagnostico_ref: # si no existe, usa null
            codigo_cie10 = None
        
        # 40% de pacientes activos (sin fecha de alta)
        fecha_alta = row["Discharge Date"] if (index % 100) >= 40 else None
        
        # crea el paciente
        paciente = Paciente(
            nombre=nombre_cifrado, # nombre cifrado
            edad=int(row["Age"]), # edad
            genero=row["Gender"], # genero
            tipo_sangre=row["Blood Type"], # tipo de sangre
            diagnostico=diagnostico_cifrado, # diagnostico cifrado
            codigo_cie10=codigo_cie10, # codigo cie10
            fecha_admision=row["Date of Admission"], # fecha de admision
            doctor_id=None, # doctor_id (se asignara despues)
            hospital=row["Hospital"], # hospital
            proveedor_seguro=row["Insurance Provider"], # proveedor de seguro
            monto_facturado=monto_cifrado, # monto cifrado
            numero_habitacion=int(row["Room Number"]), # numero de habitacion
            tipo_admision=row["Admission Type"], # tipo de admision
            fecha_alta=fecha_alta, # fecha de alta (null para activos)
            medicacion=medicacion_cifrado, # medicacion cifrada
            resultado_test=resultado_cifrado # resultado cifrado
        )
        db.add(paciente) # agrega a la sesion
        contador += 1 # incrementa contador
    
    db.commit() # confirma los cambios
    print(f"se cargaron {contador} pacientes")
    return contador


def crear_usuarios_iniciales(db: Session) -> int: # crea usuarios iniciales

    # Vaciar primero la tabla de auditoría que depende de usuarios
    db.execute(text("DELETE FROM audit_logs;"))
    db.execute(text("DELETE FROM usuarios;"))
    db.commit()
    
    usuarios = [ # lista de usuarios a crear
        {
            "nombre": "Admin Sistema",
            "email": "admin@criptomed.com",
            "password": "admin123",
            "rol": RolEnum.admin
        },
        {
            "nombre": "Dr. Juan Perez",
            "email": "doctor@criptomed.com",
            "password": "doctor123",
            "rol": RolEnum.doctor
        },
        {
            "nombre": "Maria Lopez",
            "email": "admin@clinica.com",
            "password": "admin123",
            "rol": RolEnum.administrativo
        },
        {
            "nombre": "Auditor Externo",
            "email": "auditor@criptomed.com",
            "password": "auditor123",
            "rol": RolEnum.auditor
        }
    ]
    
    contador = 0 # contador de usuarios creados
    
    for usuario_data in usuarios: # itera sobre cada usuario
        # verifica si ya existe el email
        existe = db.query(Usuario).filter(Usuario.email == usuario_data["email"]).first()
        if existe: # si ya existe, salta
            continue
        
        # crea el usuario
        usuario = Usuario(
            nombre=usuario_data["nombre"], # nombre
            email=usuario_data["email"], # email
            password_hash=hash_password(usuario_data["password"]), # password hasheado
            rol=usuario_data["rol"], # rol
            activo=True # activo
        )
        db.add(usuario) # agrega a la sesion
        contador += 1 # incrementa contador
    
    db.commit() # confirma los cambios
    print(f"se crearon {contador} usuarios iniciales")
    return contador


def verificar_datos(db: Session) -> None: # verifica que los datos se cargaron correctamente
    print("\n--- verificacion de datos ---")
    
    # cuenta usuarios
    count_usuarios = db.query(Usuario).count()
    print(f"usuarios en bd: {count_usuarios}")
    
    # cuenta pacientes
    count_pacientes = db.query(Paciente).count()
    print(f"pacientes en bd: {count_pacientes}")
    
    # cuenta diagnosticos
    count_diagnosticos = db.query(DiagnosticoCIE10).count()
    print(f"diagnosticos cie10 en bd: {count_diagnosticos}")
    
    # muestra un ejemplo de paciente descifrado
    paciente = db.query(Paciente).first()
    if paciente: # si existe al menos un paciente
        print(f"\nejemplo de paciente:")
        print(f"  nombre (cifrado): {paciente.nombre[:50]}...")
        print(f"  nombre (descifrado): {decrypt(paciente.nombre)[:50]}...") # descifra el nombre
        print(f"  edad: {paciente.edad}")
        print(f"  genero: {paciente.genero}")


def main(): # funcion principal
    print("=== script de carga de datos para criptomed ===")
    print("este script cargara los datos de ejemplo en la base de datos\n")
    
    # crea la sesion de base de datos
    db = SessionLocal()
    
    try:
        # carga diagnosticos cie10
        print("--- paso 1: cargar diagnosticos cie10 ---")
        cargar_diagnosticos_cie10(db)
        
        # carga pacientes
        print("\n--- paso 2: cargar pacientes ---")
        cargar_pacientes(db)
        
        # crea usuarios iniciales
        print("\n--- paso 3: crear usuarios iniciales ---")
        crear_usuarios_iniciales(db)
        
        # verifica datos
        verificar_datos(db)
        
        print("\n=== carga de datos completada exitosamente ===")
        
    except Exception as e: # captura errores
        print(f"error durante la carga de datos: {e}")
        db.rollback() # revierte cambios en caso de error
        raise
    finally:
        db.close() # cierra la sesion


if __name__ == "__main__": # ejecuta la funcion principal si el script se ejecuta directamente
    main() # ejecuta la funcion principal
