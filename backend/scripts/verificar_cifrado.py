import sys
from pathlib import Path

# Configurar el path para poder importar los módulos de 'app'
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.models import Paciente
from app.crypto import decrypt

def verificar_datos_reposo():
    db = SessionLocal()
    pacientes = db.query(Paciente).limit(3).all()
    
    if not pacientes:
        print("No hay pacientes en la base de datos para verificar.")
        db.close()
        return

    print("\n=== VERIFICACIÓN DE ENCRIPTACIÓN AES-256 ===")
    
    for p in pacientes:
        print(f"\nID Paciente: {p.id}")
        
        print("  [DATOS EN CRUDO (EN REPOSO)]")
        # Mostramos los primeros 60 caracteres para no saturar la consola con cadenas largas en base64
        print(f"  Nombre cifrado      : {str(p.nombre)[:60]}...")
        print(f"  Diagnóstico cifrado : {str(p.diagnostico)[:60]}...")
        print(f"  Medicamentos cifrado: {str(p.medicacion)[:60]}...")
        
        print("\n  [DATOS DESCIFRADOS POR LA APLICACIÓN]")
        print(f"  Nombre en claro      : {decrypt(p.nombre)}")
        print(f"  Diagnóstico en claro : {decrypt(p.diagnostico)}")
        print(f"  Medicamentos en claro: {decrypt(p.medicacion)}")
        
        print("-" * 60)
        
    db.close()

if __name__ == "__main__":
    verificar_datos_reposo()