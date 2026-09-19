from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime as dt

from app.database import get_db
from app.models import Paciente, RolEnum, Usuario, AccionEnum, AuditLog
from app.schemas import PacienteCreate, PacienteResponse
from app.rbac import require_role, get_current_user
from app.crypto import encrypt, decrypt  # Importamos las funciones de cifrado

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

# Acceso permitido para administradores, doctores y administrativos
autorizado = Depends(require_role([RolEnum.admin, RolEnum.doctor, RolEnum.administrativo]))

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


@router.get("", response_model=List[PacienteResponse])
def listar_pacientes(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene la lista de pacientes según el rol del usuario."""
    query = db.query(Paciente)
    
    # Si es doctor, solo ver sus pacientes asignados
    if current_user.rol == RolEnum.doctor:
        print(f"Doctor ID: {current_user.id}")
        query = query.filter(Paciente.doctor_id == current_user.id)
        print(f"Query: {query}")
    
    pacientes_db = (
        query
        .order_by(Paciente.fecha_admision.desc())  # Trae primero los registros más recientes
        .limit(5000)  # Aumentado a 5000 para demostración
        .all()
    )
    print(f"Pacientes encontrados: {len(pacientes_db)}")
    return [formatear_paciente_respuesta(p) for p in pacientes_db]


@router.get("/me", response_model=PacienteResponse)
def mi_historial(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene el historial del paciente autenticado."""
    if current_user.rol != RolEnum.paciente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo para pacientes"
        )
    paciente = db.query(Paciente).filter(Paciente.usuario_id == current_user.id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el historial del paciente"
        )
    return formatear_paciente_respuesta(paciente)


@router.get("/doctores")
def listar_doctores(db: Session = Depends(get_db)):
    """Lista todos los doctores activos para el dropdown de transferencia."""
    doctores = db.query(Usuario).filter(
        Usuario.rol == RolEnum.doctor,
        Usuario.activo == True
    ).all()
    return [
        {
            "id": doc.id,
            "nombre": doc.nombre,
            "email": doc.email
        }
        for doc in doctores
    ]


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


@router.patch("/{paciente_id}/transferir-doctor")
async def transferir_doctor(
    paciente_id: UUID,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Transfiere un paciente a otro doctor. Solo puede hacerlo el propio paciente o un admin."""
    print(f"Transferencia solicitada: paciente_id={paciente_id}, user_id={current_user.id}, user_rol={current_user.rol}")
    
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )

    print(f"Paciente encontrado: {paciente.id}, usuario_id={paciente.usuario_id}")

    # Obtener nuevo_doctor_id del cuerpo del request
    body = await request.json()
    nuevo_doctor_id = body.get("nuevo_doctor_id")
    
    print(f"Nuevo doctor ID: {nuevo_doctor_id}")
    
    if not nuevo_doctor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere nuevo_doctor_id"
        )

    # Verificar que el nuevo doctor existe y es un doctor
    nuevo_doctor = db.query(Usuario).filter(
        Usuario.id == nuevo_doctor_id,
        Usuario.rol == RolEnum.doctor
    ).first()
    if not nuevo_doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor no encontrado"
        )

    print(f"Nuevo doctor encontrado: {nuevo_doctor.id}, nombre={nuevo_doctor.nombre}")

    # Permiso: admin, o el propio paciente autorizando el cambio
    es_admin = current_user.rol == RolEnum.admin
    es_el_mismo_paciente = paciente.usuario_id == current_user.id
    print(f"Permisos: es_admin={es_admin}, es_el_mismo_paciente={es_el_mismo_paciente}")
    
    if not (es_admin or es_el_mismo_paciente):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para transferir este paciente"
        )

    doctor_anterior = paciente.doctor_id
    paciente.doctor_id = nuevo_doctor_id
    db.commit()

    # Registrar en log de auditoría
    log = AuditLog(
        usuario_id=current_user.id,
        accion=AccionEnum.transferencia,
        recurso=f"paciente:{paciente_id}",
        detalle=f"doctor_anterior={doctor_anterior}, doctor_nuevo={nuevo_doctor_id}",
        ip_origen=request.client.host if request.client else "127.0.0.1",
        timestamp=dt.utcnow()
    )
    db.add(log)
    db.commit()

    return {
        "mensaje": "Paciente transferido correctamente",
        "nuevo_doctor_id": nuevo_doctor_id,
        "doctor_anterior_id": doctor_anterior
    }