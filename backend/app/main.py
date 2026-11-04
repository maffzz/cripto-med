import sys
from pathlib import Path
import os
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.audit import AuditMiddleware
from app.config import JWT_SECRET, ENV, ALLOWED_ORIGINS
from app.limiter import limiter
from app.security_headers import SecurityHeadersMiddleware
from app.routers import auth, usuarios, pacientes, audit_logs

# Determinar modo de ejecución: en producción se desactivan docs interactivos (OWASP)
is_production = (ENV == "production")

app = FastAPI(
    title="CriptoMed",
    description="Historiales clínicos con RBAC, cifrado y auditoría — DS3031",
    version="0.1.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. Middleware de Cabeceras de Seguridad HTTP (HSTS, CSP, nosniff, no-store, DENY)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Configuración restrictiva de CORS (Paso 1.6a)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Forwarded-For"],
)

# 3. Middleware de auditoría forense con cadena de hashes SHA-256
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
        "docs": "Visita /docs para probar los endpoints de autenticación" if not is_production else "Deshabilitado en producción"
    }
