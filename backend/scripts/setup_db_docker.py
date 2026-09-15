"""
script simplificado para configurar base de datos postgresql en docker
este script solo crea las tablas usando sqlalchemy
docker compose se encarga de crear la base de datos y usuario automaticamente
"""

import sys # para manejar errores y salir del script
from pathlib import Path # para rutas de archivos

# crear tablas usando sqlalchemy
def crear_tablas():
    """crea las tablas usando los modelos de sqlalchemy"""
    print("=== script de configuracion de tablas para criptomed (docker) ===")
    print("este script creara las tablas en postgresql usando docker")
    print("")
    
    try:
        # agrega el directorio backend al path para poder importar los modelos
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        # importa los modelos y la configuracion de la base de datos
        from app.database import Base, engine
        from app.models import Usuario, Paciente, DiagnosticoCIE10, AuditLog
        
        # crea todas las tablas definidas en los modelos
        Base.metadata.create_all(bind=engine)
        print("tablas creadas exitosamente:")
        print("  - usuarios")
        print("  - pacientes")
        print("  - diagnosticos_cie10")
        print("  - audit_logs")
        
    except Exception as e:
        print(f"error al crear tablas: {e}")
        print("asegurate de que:")
        print("  1. docker compose este corriendo (docker compose up -d)")
        print("  2. el archivo .env tenga la conexion correcta a postgresql")
        print("  3. las dependencias esten instaladas (pip install -r requirements.txt)")
        return False
    
    return True

# funcion principal
def main():
    """funcion principal que ejecuta el proceso de configuracion"""
    
    # crear tablas
    if not crear_tablas():
        sys.exit(1) # sale si falla la creacion de tablas
    
    print("\n=== configuracion completada exitosamente ===")
    print("ahora puedes ejecutar el script seed_db.py para cargar los datos de ejemplo")

if __name__ == "__main__":
    main() # ejecuta la funcion principal si el script se ejecuta directamente