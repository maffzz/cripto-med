"""
Módulo de Auditoría de CriptoMed.
Implementa trazabilidad e inmutabilidad mediante cadena criptográfica de hashes (SHA-256).
Estándares:
- NIST SP 800-92: Guide to Computer Security Log Management.
- OWASP Logging Cheat Sheet.
"""

import hashlib
from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID
from jose import jwt, JWTError
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from app.database import SessionLocal
from app.models import AuditLog, Usuario, AccionEnum
from app.config import JWT_SECRET, JWT_ALGORITHM

GENESIS_HASH = "0" * 64
ADVISORY_LOCK_ID = 42424242
EXCLUDE_PATHS = ["/docs", "/redoc", "/openapi.json", "/health", "/favicon.ico", "/pacientes/transferir-doctor"]


def format_iso_utc(ts: datetime) -> str:
    """Formatea un datetime en ISO-8601 UTC estandarizado para hashing."""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    else:
        ts = ts.astimezone(timezone.utc)
    return ts.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def calcular_hash_log(
    hash_prev: str,
    usuario_id: Optional[Union[UUID, str]],
    accion: str,
    recurso: str,
    timestamp_iso: str,
    ip_origen: Optional[str],
    detalle: Optional[str] = None
) -> str:
    """Calcula hash_actual = SHA-256(hash_prev|usuario_id|accion|recurso|ts_iso|ip|detalle)."""
    uid_str = str(usuario_id) if usuario_id else ""
    partes = [
        hash_prev,
        uid_str,
        accion,
        recurso,
        timestamp_iso,
        ip_origen or "127.0.0.1",
        detalle or ""
    ]
    payload = "|".join(partes)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def log_action(
    db: Session,
    accion: Union[AccionEnum, str],
    recurso: str,
    usuario_id: Optional[UUID] = None,
    ip_origen: Optional[str] = None,
    detalle: Optional[str] = None,
) -> AuditLog:
    """
    Registra un evento de auditoría dentro de UNA transacción atómica serializada.
    
    1. Adquiere pg_advisory_xact_lock para evitar condiciones de carrera entre escrituras concurrentes.
    2. Obtiene el hash_actual del último registro por seq (o GENESIS_HASH).
    3. Genera timestamp UTC en Python y calcula hash_actual con SHA-256.
    4. Inserta el registro y confirma la transacción.
    """
    # 1. Serializar escrituras concurrentes con advisory lock en PostgreSQL
    try:
        db.execute(text(f"SELECT pg_advisory_xact_lock({ADVISORY_LOCK_ID});"))
    except Exception:
        # Si se ejecuta en SQLite u otro motor durante tests, continuar normalmente
        pass

    # 2. Leer el hash del último registro insertado por número de secuencia
    ultimo_log = db.query(AuditLog).order_by(AuditLog.seq.desc()).first()
    hash_prev = ultimo_log.hash_actual if ultimo_log and ultimo_log.hash_actual else GENESIS_HASH

    # 3. Generar timestamp en Python en UTC
    ts_utc = datetime.now(timezone.utc)
    ts_iso = format_iso_utc(ts_utc)

    # Normalizar acción
    if isinstance(accion, AccionEnum):
        accion_enum = accion
        accion_str = accion.value
    else:
        accion_str = str(accion)
        try:
            accion_enum = AccionEnum(accion_str)
        except ValueError:
            accion_enum = AccionEnum.lectura

    ip_final = ip_origen or "127.0.0.1"
    detalle_final = detalle or ""

    # 4. Calcular hash_actual SHA-256
    hash_actual = calcular_hash_log(
        hash_prev=hash_prev,
        usuario_id=usuario_id,
        accion=accion_str,
        recurso=recurso,
        timestamp_iso=ts_iso,
        ip_origen=ip_final,
        detalle=detalle_final
    )

    # 5. Insertar en audit_logs
    log_entry = AuditLog(
        usuario_id=usuario_id,
        accion=accion_enum,
        recurso=recurso,
        timestamp=ts_utc,
        ip_origen=ip_final,
        detalle=detalle_final if detalle_final else None,
        hash_prev=hash_prev,
        hash_actual=hash_actual,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def extract_client_ip(request: Request) -> str:
    """Extrae la IP real del cliente respetando X-Forwarded-For del edge Nginx."""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware para interceptar peticiones y registrarlas en la cadena de auditoría."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Omitir rutas públicas, docs y endpoints con auditoría explícita
        if any(path.startswith(exc) for exc in EXCLUDE_PATHS):
            return await call_next(request)

        response = await call_next(request)

        # Registrar peticiones exitosas de usuarios autenticados
        if response.status_code < 400:
            auth_header = request.headers.get("Authorization")

            if auth_header and auth_header.startswith("Bearer "):
                db = SessionLocal()
                try:
                    token = auth_header.split(" ")[1]
                    try:
                        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                        email: str = payload.get("sub")
                        if email:
                            usuario = db.query(Usuario).filter(Usuario.email == email).first()
                            if usuario:
                                method_map = {
                                    "GET": AccionEnum.lectura,
                                    "POST": AccionEnum.edicion,
                                    "PUT": AccionEnum.edicion,
                                    "PATCH": AccionEnum.edicion,
                                    "DELETE": AccionEnum.borrado,
                                }
                                accion = method_map.get(request.method, AccionEnum.lectura)
                                ip_origen = extract_client_ip(request)

                                log_action(
                                    db=db,
                                    accion=accion,
                                    recurso=f"{request.method} {path}",
                                    usuario_id=usuario.id,
                                    ip_origen=ip_origen,
                                    detalle=None
                                )
                    except (JWTError, ValueError):
                        pass
                except Exception as e:
                    print(f"Error en middleware de auditoría: {e}")
                finally:
                    db.close()

        return response
