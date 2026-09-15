from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship # para definir relaciones entre modelos
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid_lib # libreria uuid para generar ids
import enum # para crear enums en python
from datetime import datetime as dt # alias distinto para evitar colisión con sqlalchemy

from app.database import Base # base declarativa para los modelos


# enum para roles de usuario
class RolEnum(enum.Enum):
    admin = "admin" # administrador tiene todos los permisos
    doctor = "doctor" # doctor puede ver y editar pacientes asignados
    administrativo = "administrativo" # personal administrativo ve datos basicos y facturacion
    auditor = "auditor" # auditor solo puede ver logs de auditoria


# enum para acciones de auditoria
class AccionEnum(enum.Enum):
    login = "login" # inicio de sesion
    lectura = "lectura" # consulta de datos
    edicion = "edicion" # modificacion de datos
    borrado = "borrado" # eliminacion de datos


# modelo de usuario
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False) # hash con bcrypt/Argon2
    rol = Column(SQLEnum(RolEnum), nullable=False)
    activo = Column(Boolean, default=True) # para revocación de accesos
    creado_en = Column(DateTime, default=dt.utcnow)

    pacientes_asignados = relationship("Paciente", back_populates="doctor")
    audit_logs = relationship("AuditLog", back_populates="usuario")


# modelo de paciente
class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    nombre = Column(String, nullable=False) # cifrado en capa de aplicación (AES-256)
    edad = Column(Integer, nullable=False)
    genero = Column(String, nullable=False)
    tipo_sangre = Column(String)
    diagnostico = Column(String) # cifrado en capa de aplicación
    codigo_cie10 = Column(String, ForeignKey("diagnosticos_cie10.codigo"))
    fecha_admision = Column(DateTime, nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    hospital = Column(String)
    proveedor_seguro = Column(String)
    monto_facturado = Column(String) # cifrado -> se guarda como texto cifrado, NO como Numeric
    numero_habitacion = Column(String)
    tipo_admision = Column(String)
    fecha_alta = Column(DateTime)
    medicacion = Column(String) # cifrado en capa de aplicación
    resultado_test = Column(String) # cifrado en capa de aplicación

    doctor = relationship("Usuario", back_populates="pacientes_asignados")
    diagnostico_cie10_rel = relationship("DiagnosticoCIE10", back_populates="pacientes")


# modelo de diagnostico cie10
class DiagnosticoCIE10(Base):
    __tablename__ = "diagnosticos_cie10"

    codigo = Column(String, primary_key=True)
    descripcion = Column(String, nullable=False)

    pacientes = relationship("Paciente", back_populates="diagnostico_cie10_rel")


# modelo de log de auditoria
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    accion = Column(SQLEnum(AccionEnum), nullable=False)
    recurso = Column(String, nullable=False) # ej: "paciente:uuid"
    timestamp = Column(DateTime, default=dt.utcnow, nullable=False)
    ip_origen = Column(String)

    usuario = relationship("Usuario", back_populates="audit_logs")