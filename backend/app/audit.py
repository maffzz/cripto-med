from datetime import datetime
from typing import Optional
from uuid import UUID
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from app.database import SessionLocal
from app.models import AuditLog, Usuario
from app.config import JWT_SECRET, JWT_ALGORITHM

EXCLUDE_PATHS = ["/docs", "/redoc", "/openapi.json", "/health", "/favicon.ico", "/auth/login", "/pacientes/transferir-doctor"]  # Rutas que no se auditarán


def log_action(
    db: Session,
    accion: str,
    recurso: str,
    usuario_id: Optional[UUID] = None,
    ip_origen: Optional[str] = None,
) -> None:
    """Registra una entrada directa en la tabla audit_logs."""
    try:
        log_entry = AuditLog(
            usuario_id=usuario_id,
            accion=accion,
            recurso=recurso,
            ip_origen=ip_origen or "127.0.0.1",
            timestamp=datetime.utcnow(),
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error al escribir en el log de auditoría: {e}")


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware para interceptar peticiones y registrarlas automáticamente."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Omitir rutas públicas o documentación
        if any(path.startswith(exc) for exc in EXCLUDE_PATHS):
            return await call_next(request)

        # Omitir específicamente el endpoint de transferencia
        if "transferir-doctor" in path:
            return await call_next(request)

        response = await call_next(request)

        # Registrar peticiones procesadas exitosamente
        if response.status_code < 400:
            auth_header = request.headers.get("Authorization")

            # Solo registrar logs si hay un usuario autenticado
            if auth_header and auth_header.startswith("Bearer "):
                db = SessionLocal()
                try:
                    # Extraer y decodificar el Token JWT
                    token = auth_header.split(" ")[1]
                    try:
                        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                        email: str = payload.get("sub")
                        if email:
                            # Obtenemos el UUID del usuario consultando por su email
                            usuario = db.query(Usuario).filter(Usuario.email == email).first()
                            if usuario:
                                # Mapear método HTTP a tipo de acción
                                method_map = {
                                    "GET": "lectura",
                                    "POST": "edicion",
                                    "PUT": "edicion",
                                    "PATCH": "edicion",
                                    "DELETE": "borrado",
                                }
                                accion = method_map.get(request.method, request.method.lower())

                                ip_origen = request.client.host if request.client else "127.0.0.1"

                                log_action(
                                    db=db,
                                    accion=accion,
                                    recurso=f"{request.method} {path}",
                                    usuario_id=usuario.id,
                                    ip_origen=ip_origen,
                                )
                    except (JWTError, ValueError):
                        pass
                except Exception as e:
                    # No fallar el request si hay error en el logging
                    print(f"Error en middleware de auditoría: {e}")
                finally:
                    db.close()

        return response