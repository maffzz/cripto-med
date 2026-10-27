"""
script simplificado para configurar base de datos postgresql en docker
este script usa DATABASE_URL (rol dueño) para crear tablas
"""

import sys
import os
from pathlib import Path

print("Script iniciado...")
print(f"Python version: {sys.version}")
print(f"Working dir: {os.getcwd()}")

def crear_tablas():
    """crea las tablas usando sql directo"""
    print("=== script de configuracion de tablas para criptomed (docker) ===")
    print("este script creara las tablas en postgresql usando sql directo")
    print("")
    
    try:
        print("Importando sqlalchemy...")
        from sqlalchemy import create_engine, text
        print("SQLAlchemy importado OK")
        
        # Usa DATABASE_URL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("Error: DATABASE_URL no está definido en .env")
            return False
        
        print(f"DATABASE_URL: {db_url[:20]}...")
        
        # Agrega +psycopg si no está presente
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://")
        
        print(f"DB URL con driver: {db_url[:20]}...")
        
        # Crea engine
        print("Creando engine...")
        engine = create_engine(db_url)
        print("Engine creado OK")
        
        # Define SQL para crear tablas
        tables_sql = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(20) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS pacientes (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            fecha_nacimiento DATE NOT NULL,
            dni VARCHAR(20) UNIQUE NOT NULL,
            doctor_id INTEGER REFERENCES usuarios(id),
            diagnostico TEXT,
            medicacion TEXT,
            resultado_test TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS diagnosticos_cie10 (
            codigo VARCHAR(10) PRIMARY KEY,
            descripcion TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id),
            accion VARCHAR(100) NOT NULL,
            tabla_afectada VARCHAR(50),
            registro_id INTEGER,
            ip_origen VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Ejecuta SQL
        with engine.connect() as conn:
            for statement in tables_sql.split(';'):
                statement = statement.strip()
                if statement:
                    conn.execute(text(statement))
            conn.commit()
        
        print("tablas creadas exitosamente:")
        print("  - usuarios")
        print("  - pacientes")
        print("  - diagnosticos_cie10")
        print("  - audit_logs")
        
    except Exception as e:
        print(f"error al crear tablas: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """funcion principal que ejecuta el proceso de configuracion"""
    
    # crear tablas
    if not crear_tablas():
        sys.exit(1)
    
    print("\n=== configuracion completada exitosamente ===")
    print("ahora puedes ejecutar el script seed_db.py para cargar los datos de ejemplo")

if __name__ == "__main__":
    main()
