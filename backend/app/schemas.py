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

class PacienteCreate(PacienteBase):
    # Campos que el usuario envía en claro al crear
    nombre_descifrado: str
    diagnostico_descifrado: Optional[str] = None
    monto_facturado_descifrado: Optional[str] = None
    medicacion_descifrado: Optional[str] = None
    resultado_test_descifrado: Optional[str] = None

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

# --- Esquemas de Auditoría ---

class AuditLogBase(BaseModel):
    accion: AccionEnum
    recurso: str
    ip_origen: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    usuario_id: UUID

class AuditLogResponse(AuditLogBase):
    id: UUID
    usuario_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)