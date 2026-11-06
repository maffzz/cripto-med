from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import AuditLog, Paciente, Usuario, RolEnum, AccionEnum
from app.rbac import require_role

router = APIRouter(prefix="/audit-logs", tags=["Auditoría"])

# Restricción exclusiva para Auditor y Administrador (NIST SP 800-92 / RBAC)
autorizado = Depends(require_role([RolEnum.admin, RolEnum.auditor]))

# Zona horaria de Lima (UTC-5) sin horario de verano
LIMA_TZ = timezone(timedelta(hours=-5))


class AuditLogResponse(BaseModel):
    id: UUID
    seq: Optional[int] = None
    hash_prev: Optional[str] = None
    hash_actual: Optional[str] = None
    usuario_id: Optional[UUID] = None
    accion: str
    recurso: str
    ip_origen: Optional[str] = None
    detalle: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAuditLogs(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AuditLogResponse]


class AlertaItem(BaseModel):
    tipo: str
    nivel: str
    descripcion: str
    usuario_id: Optional[UUID] = None
    recurso: Optional[str] = None
    ip_origen: Optional[str] = None
    conteo: Optional[int] = None
    timestamp: Optional[datetime] = None
    detalles: Optional[Dict[str, Any]] = None


class ReporteAlertas(BaseModel):
    total_alertas: int
    generado_en: datetime
    alertas: List[AlertaItem]


class MetricasOficial(BaseModel):
    """Métricas reales del sistema para el Dashboard Oficial (admin only)."""
    # Pacientes
    total_pacientes: int
    pacientes_activos: int
    pacientes_dados_alta: int
    # Usuarios
    total_usuarios: int
    usuarios_activos: int
    usuarios_por_rol: Dict[str, int]
    # Actividad (últimas 24 h y 7 días)
    accesos_24h: int
    accesos_7d: int
    logins_fallidos_24h: int
    bloqueos_24h: int
    exportaciones_7d: int
    accesos_emergencia_7d: int
    # Logs
    total_logs: int
    ultimo_log_ts: Optional[datetime]
    # Generado
    generado_en: datetime


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


@router.get("/metricas", response_model=MetricasOficial, dependencies=[autorizado])
def obtener_metricas(db: Session = Depends(get_db)):
    """
    Métricas reales del sistema para el Dashboard Oficial.
    Solo accesible para admin y auditor.
    Los datos se calculan en tiempo real desde audit_logs, pacientes y usuarios.
    """
    now = datetime.now(timezone.utc)
    hace_24h = (now - timedelta(hours=24)).replace(tzinfo=None)
    hace_7d = (now - timedelta(days=7)).replace(tzinfo=None)

    # --- Pacientes ---
    total_pacientes = db.query(func.count(Paciente.id)).scalar() or 0
    pacientes_activos = db.query(func.count(Paciente.id)).filter(Paciente.fecha_alta.is_(None)).scalar() or 0
    pacientes_dados_alta = total_pacientes - pacientes_activos

    # --- Usuarios ---
    total_usuarios = db.query(func.count(Usuario.id)).scalar() or 0
    usuarios_activos = db.query(func.count(Usuario.id)).filter(Usuario.activo.is_(True)).scalar() or 0

    usuarios_por_rol_rows = (
        db.query(Usuario.rol, func.count(Usuario.id))
        .group_by(Usuario.rol)
        .all()
    )
    usuarios_por_rol = {
        (row[0].value if hasattr(row[0], 'value') else str(row[0])): row[1]
        for row in usuarios_por_rol_rows
    }

    # --- Actividad desde audit_logs ---
    def count_accion(accion: AccionEnum, desde=None):
        q = db.query(func.count(AuditLog.id)).filter(AuditLog.accion == accion)
        if desde:
            q = q.filter(AuditLog.timestamp >= desde)
        return q.scalar() or 0

    accesos_24h = (
        db.query(func.count(AuditLog.id))
        .filter(AuditLog.accion == AccionEnum.lectura, AuditLog.timestamp >= hace_24h)
        .scalar() or 0
    )
    accesos_7d = (
        db.query(func.count(AuditLog.id))
        .filter(AuditLog.accion == AccionEnum.lectura, AuditLog.timestamp >= hace_7d)
        .scalar() or 0
    )
    logins_fallidos_24h = count_accion(AccionEnum.login_fallido, hace_24h)
    bloqueos_24h = count_accion(AccionEnum.bloqueo, hace_24h)
    exportaciones_7d = count_accion(AccionEnum.exportacion, hace_7d)
    accesos_emergencia_7d = count_accion(AccionEnum.acceso_emergencia, hace_7d)

    # --- Logs totales y último ---
    total_logs = db.query(func.count(AuditLog.id)).scalar() or 0
    ultimo_log = db.query(AuditLog).order_by(AuditLog.seq.desc()).first()
    ultimo_log_ts = ultimo_log.timestamp if ultimo_log else None

    return MetricasOficial(
        total_pacientes=total_pacientes,
        pacientes_activos=pacientes_activos,
        pacientes_dados_alta=pacientes_dados_alta,
        total_usuarios=total_usuarios,
        usuarios_activos=usuarios_activos,
        usuarios_por_rol=usuarios_por_rol,
        accesos_24h=accesos_24h,
        accesos_7d=accesos_7d,
        logins_fallidos_24h=logins_fallidos_24h,
        bloqueos_24h=bloqueos_24h,
        exportaciones_7d=exportaciones_7d,
        accesos_emergencia_7d=accesos_emergencia_7d,
        total_logs=total_logs,
        ultimo_log_ts=ultimo_log_ts,
        generado_en=now,
    )


@router.get("/alertas", response_model=ReporteAlertas, dependencies=[autorizado])
def detectar_alertas(
    horas: int = Query(24, ge=1, le=168, description="Ventana de tiempo para análisis de accesos fuera de horario (horas)"),
    umbral_lecturas: int = Query(30, ge=1, le=1000, description="Umbral de lecturas de recursos distintos en 1 hora"),
    db: Session = Depends(get_db),
):
    """
    Motor de detección de anomalías y alertas tempranas de seguridad (NIST SP 800-61 / OWASP).
    
    Reglas evaluadas:
    1. FUERZA_BRUTA_LOGIN: Usuarios o identidades con 5 o más intentos fallidos en los últimos 10 minutos.
    2. ACCESO_FUERA_DE_HORARIO: Consultas a historias clínicas fuera de 07:00 a 21:00 hora de Lima (UTC-5).
    3. VOLUMEN_ANOMALO_LECTURAS: Usuarios que hayan consultado más de 'umbral_lecturas' pacientes distintos en 1 hora.
    """
    now = datetime.now(timezone.utc)
    alertas: List[AlertaItem] = []

    # -------------------------------------------------------------
    # Regla 1: Fuerza Bruta en Autenticación (5+ fallos en 10 min)
    # -------------------------------------------------------------
    ventana_fb = now - timedelta(minutes=10)
    # AuditLog.timestamp puede ser naive o aware dependiendo de la BD
    logs_fb = (
        db.query(AuditLog)
        .filter(
            AuditLog.accion == AccionEnum.login_fallido,
            AuditLog.timestamp >= ventana_fb.replace(tzinfo=None)
        )
        .all()
    )

    conteo_fb: Dict[str, Dict[str, Any]] = {}
    for log in logs_fb:
        clave = str(log.usuario_id) if log.usuario_id else (log.detalle or log.ip_origen or "anonimo")
        if clave not in conteo_fb:
            conteo_fb[clave] = {"usuario_id": log.usuario_id, "ip": log.ip_origen, "logs": []}
        conteo_fb[clave]["logs"].append(log)

    for clave, datos in conteo_fb.items():
        if len(datos["logs"]) >= 5:
            alertas.append(AlertaItem(
                tipo="FUERZA_BRUTA_LOGIN",
                nivel="ALTA",
                descripcion=f"Se detectaron {len(datos['logs'])} intentos fallidos de autenticación en los últimos 10 minutos para '{clave}'.",
                usuario_id=datos["usuario_id"],
                ip_origen=datos["ip"],
                conteo=len(datos["logs"]),
                timestamp=datos["logs"][-1].timestamp,
                detalles={"intentos": len(datos["logs"]), "ventana_minutos": 10}
            ))

    # -------------------------------------------------------------
    # Regla 2: Acceso Fuera de Horario Laboral (07:00-21:00 UTC-5)
    # -------------------------------------------------------------
    ventana_horario = now - timedelta(hours=horas)
    logs_lectura = (
        db.query(AuditLog)
        .filter(
            AuditLog.accion == AccionEnum.lectura,
            AuditLog.timestamp >= ventana_horario.replace(tzinfo=None)
        )
        .all()
    )

    for log in logs_lectura:
        ts = log.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        ts_lima = ts.astimezone(LIMA_TZ)
        if ts_lima.hour < 7 or ts_lima.hour >= 21:
            alertas.append(AlertaItem(
                tipo="ACCESO_FUERA_DE_HORARIO",
                nivel="MEDIA",
                descripcion=(
                    f"Lectura de recurso '{log.recurso}' realizada a las {ts_lima.strftime('%H:%M:%S')} "
                    f"(hora de Lima, UTC-5), fuera del horario operativo permitido (07:00 - 21:00)."
                ),
                usuario_id=log.usuario_id,
                recurso=log.recurso,
                ip_origen=log.ip_origen,
                timestamp=log.timestamp,
                detalles={
                    "hora_lima": ts_lima.strftime("%H:%M:%S"),
                    "fecha_lima": ts_lima.strftime("%Y-%m-%d"),
                    "recurso": log.recurso
                }
            ))

    # -------------------------------------------------------------
    # Regla 3: Volumen Anómalo de Lecturas (> N pacientes en 1 hora)
    # -------------------------------------------------------------
    ventana_volumen = now - timedelta(hours=1)
    conteo_recursos = (
        db.query(
            AuditLog.usuario_id,
            func.count(func.distinct(AuditLog.recurso)).label("total_distintos")
        )
        .filter(
            AuditLog.accion == AccionEnum.lectura,
            AuditLog.usuario_id.isnot(None),
            AuditLog.timestamp >= ventana_volumen.replace(tzinfo=None)
        )
        .group_by(AuditLog.usuario_id)
        .having(func.count(func.distinct(AuditLog.recurso)) > umbral_lecturas)
        .all()
    )

    for uid, total_distintos in conteo_recursos:
        alertas.append(AlertaItem(
            tipo="VOLUMEN_ANOMALO_LECTURAS",
            nivel="ALTA",
            descripcion=(
                f"El usuario consultó {total_distintos} recursos distintos en la última hora, "
                f"superando el umbral de seguridad permitido de {umbral_lecturas} consultas."
            ),
            usuario_id=uid,
            conteo=total_distintos,
            timestamp=now,
            detalles={
                "recursos_consultados": total_distintos,
                "umbral": umbral_lecturas,
                "ventana_horas": 1
            }
        ))

    # -------------------------------------------------------------
    # Regla 4: Accesos de Emergencia (Break-Glass) a Revisar por Auditor
    # -------------------------------------------------------------
    logs_emergencia = (
        db.query(AuditLog)
        .filter(
            AuditLog.accion == AccionEnum.acceso_emergencia,
            AuditLog.timestamp >= ventana_horario.replace(tzinfo=None)
        )
        .all()
    )
    for log in logs_emergencia:
        alertas.append(AlertaItem(
            tipo="ACCESO_EMERGENCIA_BREAK_GLASS",
            nivel="ALTA",
            descripcion=(
                f"Acceso de emergencia ('break-glass') ejecutado sobre '{log.recurso}'. "
                f"Requiere revisión y justificación médica inmediata por el auditor."
            ),
            usuario_id=log.usuario_id,
            recurso=log.recurso,
            ip_origen=log.ip_origen,
            timestamp=log.timestamp,
            detalles={
                "accion": "acceso_emergencia",
                "justificacion": log.detalle,
                "recurso": log.recurso
            }
        ))

    return ReporteAlertas(
        total_alertas=len(alertas),
        generado_en=now,
        alertas=alertas
    )
