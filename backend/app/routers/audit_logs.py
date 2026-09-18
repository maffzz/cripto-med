from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, RolEnum
from app.rbac import require_role

router = APIRouter(prefix="/audit-logs", tags=["Auditoría"])

# Restricción exclusiva para Auditor y Administrador
autorizado = Depends(require_role([RolEnum.admin, RolEnum.auditor]))


class AuditLogResponse(BaseModel):
    id: UUID
    usuario_id: Optional[UUID] = None
    accion: str
    recurso: str
    ip_origen: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAuditLogs(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AuditLogResponse]


@router.get("", response_model=PaginatedAuditLogs, dependencies=[autorizado])
def listar_logs(
    usuario_id: Optional[UUID] = Query(None, description="Filtrar por ID de usuario"),
    accion: Optional[str] = Query(None, description="Filtrar por acción (ej: lectura, login)"),
    fecha_inicio: Optional[datetime] = Query(None, description="Rango inicial (ISO 8601)"),
    fecha_fin: Optional[datetime] = Query(None, description="Rango final (ISO 8601)"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Registros por página"),
    db: Session = Depends(get_db),
):
    """Consulta histórica de eventos de auditoría del sistema."""
    query = db.query(AuditLog)

    if usuario_id:
        query = query.filter(AuditLog.usuario_id == usuario_id)
    if accion:
        query = query.filter(AuditLog.accion == accion)
    if fecha_inicio:
        query = query.filter(AuditLog.timestamp >= fecha_inicio)
    if fecha_fin:
        query = query.filter(AuditLog.timestamp <= fecha_fin)

    total = query.count()
    offset = (page - 1) * page_size
    items = (
        query.order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }