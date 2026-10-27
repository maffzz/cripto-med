import sys
from pathlib import Path
import os
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.audit import AuditMiddleware
from app.config import JWT_SECRET
from app.routers import auth, usuarios, pacientes, audit_logs

# La inicialización de la base de datos se hace con scripts/setup_db_docker.py y seed_db.py
# No se hace automáticamente al inicio del servicio para evitar dependencias innecesarias (pandas)

app = FastAPI(
    title="CriptoMed",
    description="Historiales clínicos con RBAC, cifrado y auditoría — DS3031",
    version="0.1.0",
)

# --- Configuración de CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://maffzz.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de auditoría
app.add_middleware(AuditMiddleware)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(pacientes.router)
app.include_router(audit_logs.router)

@app.get("/health")
def health() -> dict[str, str]:
    jwt_ready = "pending" if JWT_SECRET == "cambiar-en-local" else "configured"
    return {"status": "ok", "service": "criptomed", "jwt_secret": jwt_ready}

@app.get("/")
def read_root():
    return {
        "mensaje": "Bienvenido a CriptoMed API",
        "docs": "Visita /docs para probar los endpoints de autenticación"
    }

# Nota: El bloque if __name__ == "__main__" fue eliminado porque
# en Docker el comando uvicorn se ejecuta directamente desde el Dockerfile.
# El TLS ahora lo maneja el edge Nginx, no el backend.
