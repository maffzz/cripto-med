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

# Inicializar base de datos al inicio (crear tablas y usuarios si no existen)
@app.on_event("startup")
def startup_event():
    initialize_database()

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