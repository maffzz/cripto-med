from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models import RolEnum, AccionEnum

# --- Esquemas de Token (Auth) ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Esquemas de Usuario ---

class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    rol: RolEnum
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str  # Solo se usa al crear, no se devuelve en las respuestas

class UsuarioResponse(UsuarioBase):
    id: UUID
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Esquemas de Paciente ---

class PacienteBase(BaseModel):
    edad: int
    genero: str
    tipo_sangre: Optional[str] = None
    codigo_cie10: Optional[str] = None
    fecha_admision: datetime
    hospital: Optional[str] = None
    proveedor_seguro: Optional[str] = None
    numero_habitacion: Optional[str] = None
    tipo_admision: Optional[str] = None
    fecha_alta: Optional[datetime] = None
    consentimiento_fecha: Optional[datetime] = None
    consentimiento_version: Optional[str] = None

class PacienteCreate(PacienteBase):
    # Campos que el usuario envía en claro al crear
    nombre_descifrado: str
    diagnostico_descifrado: Optional[str] = None
    monto_facturado_descifrado: Optional[str] = None
    medicacion_descifrado: Optional[str] = None
    resultado_test_descifrado: Optional[str] = None

# Schema completo (admin, doctor)
class PacienteResponse(PacienteBase):
    id: UUID
    doctor_id: Optional[UUID] = None
    # Campos que la API devuelve (leyendo los getters descifrados del modelo)
    nombre_descifrado: str
    diagnostico_descifrado: Optional[str] = None
    monto_facturado_descifrado: Optional[str] = None
    medicacion_descifrado: Optional[str] = None
    resultado_test_descifrado: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Schema restringido para administrativo (sin diagnóstico, medicación, resultado_test)
class PacienteResponseBasico(PacienteBase):
    id: UUID
    doctor_id: Optional[UUID] = None
    # Solo campos básicos y facturación
    nombre_descifrado: str
    monto_facturado_descifrado: Optional[str] = None
    # NO incluye: diagnostico_descifrado, medicacion_descifrado, resultado_test_descifrado

    model_config = ConfigDict(from_attributes=True)

# --- Esquemas de Auditoría ---

class AuditLogBase(BaseModel):
    accion: AccionEnum
    recurso: str
    ip_origen: Optional[str] = None
    detalle: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    usuario_id: Optional[UUID] = None

class AuditLogResponse(AuditLogBase):
    id: UUID
    seq: Optional[int] = None
    hash_prev: Optional[str] = None
    hash_actual: Optional[str] = None
    usuario_id: Optional[UUID] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Esquemas de Trazabilidad para el Paciente ---

class AccesoLogItem(BaseModel):
    id: UUID
    seq: Optional[int] = None
    timestamp: datetime
    accion: str
    profesional_nombre: str
    profesional_rol: str
    ip_origen: Optional[str] = None
    detalle: Optional[str] = None

class PaginatedAccesosResponse(BaseModel):
    total: int
    items: List[AccesoLogItem]
    limit: int
    offset: int


# --- Esquemas de Acceso de Emergencia (Break-Glass) ---

class AccesoEmergenciaRequest(BaseModel):
    justificacion: str

