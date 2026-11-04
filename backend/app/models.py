from sqlalchemy import Column, String, Integer, BigInteger, Sequence, Boolean, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship # para definir relaciones entre modelos
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid_lib # libreria uuid para generar ids
import enum # para crear enums en python
from datetime import datetime as dt # alias distinto para evitar colisión con sqlalchemy

from app.database import Base # base declarativa para los modelos
from app.crypto import encrypt, decrypt  # funciones de cifrado y descifrado


# enum para roles de usuario
class RolEnum(enum.Enum):
    admin = "admin" # administrador tiene todos los permisos
    doctor = "doctor" # doctor puede ver y editar pacientes asignados
    administrativo = "administrativo" # personal administrativo ve datos basicos y facturacion
    auditor = "auditor" # auditor solo puede ver logs de auditoria
    paciente = "paciente" # paciente puede ver su propio historial y transferirlo a otro doctor


# enum para acciones de auditoria
class AccionEnum(enum.Enum):
    login = "login" # inicio de sesion exitoso
    login_fallido = "login_fallido" # intento de autenticacion fallido
    bloqueo = "bloqueo" # cuenta bloqueada por exceso de intentos
    lectura = "lectura" # consulta de datos
    edicion = "edicion" # modificacion de datos
    borrado = "borrado" # eliminacion de datos
    transferencia = "transferencia" # transferencia de paciente a otro doctor
    exportacion = "exportacion" # descarga o exportacion de datos del titular
    acceso_emergencia = "acceso_emergencia" # acceso break-glass de emergencia excepcional


# modelo de usuario
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False) # hash con bcrypt/Argon2
    rol = Column(SQLEnum(RolEnum), nullable=False)
    activo = Column(Boolean, default=True) # para revocación de accesos
    intentos_fallidos = Column(Integer, default=0, nullable=False)
    bloqueado_hasta = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=dt.utcnow)

    pacientes_asignados = relationship("Paciente", back_populates="doctor", foreign_keys="Paciente.doctor_id")
    paciente_cuenta = relationship("Paciente", back_populates="usuario", foreign_keys="Paciente.usuario_id", uselist=False)
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
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), unique=True, nullable=True) # FK opcional para cuenta de login del paciente
    hospital = Column(String)
    proveedor_seguro = Column(String)
    monto_facturado = Column(String) # cifrado -> se guarda como texto cifrado, NO como Numeric
    numero_habitacion = Column(String)
    tipo_admision = Column(String)
    fecha_alta = Column(DateTime)
    medicacion = Column(String) # cifrado en capa de aplicación
    resultado_test = Column(String) # cifrado en capa de aplicación
    consentimiento_fecha = Column(DateTime, nullable=True)
    consentimiento_version = Column(String, nullable=True, default="v1.0")

    doctor = relationship("Usuario", back_populates="pacientes_asignados", foreign_keys=[doctor_id])
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    diagnostico_cie10_rel = relationship("DiagnosticoCIE10", back_populates="pacientes")

    # Propiedades para cifrado/descifrado de campos sensibles con AAD (NIST SP 800-38D)
    @property
    def nombre_descifrado(self) -> str:
        return decrypt(self.nombre, aad=f"pacientes.nombre.{self.id}") if self.nombre else ""
    @nombre_descifrado.setter
    def nombre_descifrado(self, valor: str):
        self.nombre = encrypt(valor, aad=f"pacientes.nombre.{self.id}") if valor else ""

    @property
    def diagnostico_descifrado(self) -> str:
        return decrypt(self.diagnostico, aad=f"pacientes.diagnostico.{self.id}") if self.diagnostico else None
    @diagnostico_descifrado.setter
    def diagnostico_descifrado(self, valor: str):
        self.diagnostico = encrypt(valor, aad=f"pacientes.diagnostico.{self.id}") if valor else None

    @property
    def monto_facturado_descifrado(self) -> str:
        return decrypt(self.monto_facturado, aad=f"pacientes.monto_facturado.{self.id}") if self.monto_facturado else None
    @monto_facturado_descifrado.setter
    def monto_facturado_descifrado(self, valor: str):
        self.monto_facturado = encrypt(valor, aad=f"pacientes.monto_facturado.{self.id}") if valor else None

    @property
    def medicacion_descifrado(self) -> str:
        return decrypt(self.medicacion, aad=f"pacientes.medicacion.{self.id}") if self.medicacion else None
    @medicacion_descifrado.setter
    def medicacion_descifrado(self, valor: str):
        self.medicacion = encrypt(valor, aad=f"pacientes.medicacion.{self.id}") if valor else None

    @property
    def resultado_test_descifrado(self) -> str:
        return decrypt(self.resultado_test, aad=f"pacientes.resultado_test.{self.id}") if self.resultado_test else None
    @resultado_test_descifrado.setter
    def resultado_test_descifrado(self, valor: str):
        self.resultado_test = encrypt(valor, aad=f"pacientes.resultado_test.{self.id}") if valor else None

# modelo de diagnostico cie10
class DiagnosticoCIE10(Base):
    __tablename__ = "diagnosticos_cie10"

    codigo = Column(String, primary_key=True)
    descripcion = Column(String, nullable=False)

    pacientes = relationship("Paciente", back_populates="diagnostico_cie10_rel")


# modelo de log de auditoria verificable con cadena de hashes (NIST SP 800-92 / OWASP)
audit_seq = Sequence("audit_logs_seq", start=1)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    seq = Column(BigInteger, audit_seq, server_default=audit_seq.next_value(), unique=True, index=True)
    hash_prev = Column(String(64), nullable=False)
    hash_actual = Column(String(64), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    accion = Column(SQLEnum(AccionEnum), nullable=False)
    recurso = Column(String, nullable=False) # ej: "paciente:uuid"
    timestamp = Column(DateTime, default=dt.utcnow, nullable=False)
    ip_origen = Column(String)
    detalle = Column(String, nullable=True) # detalle adicional, ej: "doctor_anterior=UUID, doctor_nuevo=UUID"

    usuario = relationship("Usuario", back_populates="audit_logs")


# modelo para control de accesos de emergencia (break-glass) con ventana temporal
class AccesoEmergencia(Base):
    __tablename__ = "accesos_emergencia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    justificacion = Column(String, nullable=False)
    otorgado_en = Column(DateTime, default=dt.utcnow, nullable=False)
    expira_en = Column(DateTime, nullable=False)

    paciente = relationship("Paciente")
    doctor = relationship("Usuario")
