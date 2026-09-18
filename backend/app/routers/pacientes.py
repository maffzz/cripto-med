from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Paciente, RolEnum
from app.schemas import PacienteCreate, PacienteResponse
from app.rbac import require_role
from app.crypto import encrypt, decrypt  # Importamos tus funciones de cifrado

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

# Acceso permitido para administradores y doctores
autorizado = Depends(require_role([RolEnum.admin, RolEnum.doctor]))

def formatear_paciente_respuesta(p: Paciente) -> dict:
    """Helper para mapear el modelo de BD (cifrado) al esquema de respuesta (descifrado)"""
    return {
        "id": p.id,
        "edad": p.edad,
        "genero": p.genero,
        "tipo_sangre": p.tipo_sangre,
        "codigo_cie10": p.codigo_cie10,
        "fecha_admision": p.fecha_admision,
        "hospital": p.hospital,
        "proveedor_seguro": p.proveedor_seguro,
        "numero_habitacion": p.numero_habitacion,
        "tipo_admision": p.tipo_admision,
        "fecha_alta": p.fecha_alta,
        "doctor_id": p.doctor_id,
        # descifra al responder
        "nombre_descifrado": decrypt(p.nombre) if p.nombre else "",
        "diagnostico_descifrado": decrypt(p.diagnostico) if p.diagnostico else None,
        "monto_facturado_descifrado": decrypt(p.monto_facturado) if p.monto_facturado else None,
        "medicacion_descifrado": decrypt(p.medicacion) if p.medicacion else None,
        "resultado_test_descifrado": decrypt(p.resultado_test) if p.resultado_test else None,
    }


@router.get("", response_model=List[PacienteResponse], dependencies=[autorizado])
def listar_pacientes(db: Session = Depends(get_db)):
    """Obtiene la lista de pacientes y los descifra en memoria antes de enviarlos al cliente."""
    pacientes_db = (
        db.query(Paciente)
        .order_by(Paciente.fecha_admision.desc())  # Trae primero los registros más recientes
        .limit(50)  # Limita a los 50 registros más recientes para no saturar la respuesta
        .all()
    )
    return [formatear_paciente_respuesta(p) for p in pacientes_db]


@router.get("/{paciente_id}", response_model=PacienteResponse, dependencies=[autorizado])
def obtener_paciente(paciente_id: UUID, db: Session = Depends(get_db)):
    """Busca un paciente específico y devuelve sus datos descifrados."""
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado."
        )
    return formatear_paciente_respuesta(paciente)

@router.post("", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED, dependencies=[autorizado])
def crear_paciente(paciente_in: PacienteCreate, db: Session = Depends(get_db)):
    """Registra un nuevo paciente cifrando sus datos sensibles antes de guardarlos en PostgreSQL."""
    nuevo_paciente = Paciente(
        edad=paciente_in.edad,
        genero=paciente_in.genero,
        tipo_sangre=paciente_in.tipo_sangre,
        codigo_cie10=paciente_in.codigo_cie10,
        fecha_admision=paciente_in.fecha_admision,
        hospital=paciente_in.hospital,
        proveedor_seguro=paciente_in.proveedor_seguro,
        numero_habitacion=paciente_in.numero_habitacion,
        tipo_admision=paciente_in.tipo_admision,
        fecha_alta=paciente_in.fecha_alta,
        # Ciframos los campos sensibles usando encrypt() antes de persistir
        nombre=encrypt(paciente_in.nombre_descifrado),
        diagnostico=encrypt(paciente_in.diagnostico_descifrado) if paciente_in.diagnostico_descifrado else None,
        monto_facturado=encrypt(paciente_in.monto_facturado_descifrado) if paciente_in.monto_facturado_descifrado else None,
        medicacion=encrypt(paciente_in.medicacion_descifrado) if paciente_in.medicacion_descifrado else None,
        resultado_test=encrypt(paciente_in.resultado_test_descifrado) if paciente_in.resultado_test_descifrado else None,
    )
    
    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)
    
    # Devolvemos el registro recién creado, mapeándolo para descifrarlo en la respuesta
    return formatear_paciente_respuesta(nuevo_paciente)