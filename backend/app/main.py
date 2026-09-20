import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI # framework web para la api
from fastapi.middleware.cors import CORSMiddleware # middleware para CORS
from app.audit import AuditMiddleware # middleware para auditoria
from app.config import JWT_SECRET # secreto jwt para saber si ya se configuro
from app.routers import auth, usuarios, pacientes, audit_logs # importa los routers de autenticacion, usuarios y pacientes
from app.init_db import initialize_database # script de inicializacion automatica

app = FastAPI( # instancia principal de la aplicacion
    title="CriptoMed", # nombre que aparece en /docs
    description="Historiales clínicos con RBAC, cifrado y auditoría — DS3031", # texto de la documentacion
    version="0.1.0", # version inicial del api
)

# Inicialización de base de datos con migración forzada en segundo plano
@app.on_event("startup")
def startup_event():
    print("=== STARTUP EVENT ===", flush=True)
    import sys
    sys.stdout.flush()
    
    from app.database import engine
    from app.models import Base
    from sqlalchemy import inspect
    
    # Primero crear tablas vacías para que el servicio responda
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if not existing_tables:
        print("Creando tablas básicas...", flush=True)
        sys.stdout.flush()
        Base.metadata.create_all(bind=engine)
        print("Tablas básicas creadas", flush=True)
        sys.stdout.flush()
    
    # Cargar datos en segundo plano después de que el servicio esté live
    import threading
    def load_data_background():
        try:
            import time
            time.sleep(2)  # Esperar a que el servicio esté completamente live
            
            print("=== CARGA DE DATOS EN SEGUNDO PLANO ===", flush=True)
            sys.stdout.flush()
            
            from app.database import engine, SessionLocal
            from app.models import Base, Usuario
            from sqlalchemy import inspect
            
            # Verificar si el modelo es correcto (campo usuario_id en pacientes)
            inspector = inspect(engine)
            try:
                pacientes_columns = [col['name'] for col in inspector.get_columns('pacientes')]
                has_usuario_id = 'usuario_id' in pacientes_columns
            except:
                has_usuario_id = False
            
            if not has_usuario_id:
                print("Modelo antiguo detectado, eliminando tablas y recreando con datos...", flush=True)
                sys.stdout.flush()
                
                Base.metadata.drop_all(bind=engine)
                print("Tablas eliminadas", flush=True)
                sys.stdout.flush()
                
                Base.metadata.create_all(bind=engine)
                print("Tablas recreadas", flush=True)
                sys.stdout.flush()
                
                initialize_database()
                print("=== CARGA DE DATOS COMPLETADA ===", flush=True)
                sys.stdout.flush()
            else:
                print("Modelo actualizado correcto. No se requiere migración.", flush=True)
                sys.stdout.flush()
        except Exception as e:
            print(f"Error en carga de datos en segundo plano: {e}", flush=True)
            sys.stdout.flush()
    
    # Iniciar carga de datos en hilo separado
    thread = threading.Thread(target=load_data_background)
    thread.daemon = True
    thread.start()

# --- Configuración de CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://maffzz.github.io"
    ],  # Permitir solicitudes desde frontend local y GitHub Pages
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Middleware de auditoría
app.add_middleware(AuditMiddleware)

app.include_router(auth.router) # incluye el router de autenticacion
app.include_router(usuarios.router) # incluye el router de usuarios
app.include_router(pacientes.router) # incluye el router de pacientes
app.include_router(audit_logs.router) # incluye el router de auditoria

@app.get("/health") # endpoint publico para verificar que el servidor vive
def health() -> dict[str, str]: # no exige autenticacion
    jwt_ready = "pending" if JWT_SECRET == "cambiar-en-local" else "configured" # pending = placeholder del .env
    return {"status": "ok", "service": "criptomed", "jwt_secret": jwt_ready} # no devuelve el secreto, solo el estado

@app.get("/") # endpoint publico para verificar que el servidor vive
def read_root():
    return {
        "mensaje": "Bienvenido a CriptoMed API",
        "docs": "Visita /docs para probar los endpoints de autenticación"
    }

@app.post("/migrate-database")
def migrate_database():
    """Endpoint para forzar migración de base de datos (solo para uso manual)"""
    from app.database import engine
    from app.models import Base
    import sys
    
    try:
        print("=== MIGRACIÓN MANUAL DE BASE DE DATOS ===", flush=True)
        sys.stdout.flush()
        
        print("Eliminando todas las tablas existentes...", flush=True)
        sys.stdout.flush()
        Base.metadata.drop_all(bind=engine)
        print("Tablas eliminadas", flush=True)
        sys.stdout.flush()
        
        print("Creando tablas con el nuevo modelo...", flush=True)
        sys.stdout.flush()
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas con el nuevo modelo", flush=True)
        sys.stdout.flush()
        
        print("Ejecutando inicialización con el nuevo seed...", flush=True)
        sys.stdout.flush()
        initialize_database()
        print("Inicialización completada", flush=True)
        sys.stdout.flush()
        
        print("=== MIGRACIÓN COMPLETADA ===", flush=True)
        sys.stdout.flush()
        return {"status": "success", "message": "Migración completada"}
    except Exception as e:
        print(f"Error durante migración: {e}", flush=True)
        sys.stdout.flush()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    import os
    
    # verifica si esta en modo desarrollo o produccion
    use_https = os.getenv('USE_HTTPS', 'false').lower() == 'true'
    
    if use_https:
        # produccion: usa https con certificados autofirmados
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8443,
            ssl_keyfile="backend/certs/key.pem",
            ssl_certfile="backend/certs/cert.pem"
        )
    else:
        # desarrollo: usa http para evitar errores de certificado autofirmado en navegador
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True
        )
