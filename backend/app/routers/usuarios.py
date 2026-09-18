from uuid import UUID 
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario, RolEnum
from app.schemas import UsuarioCreate, UsuarioResponse
from app.auth import get_password_hash
from app.rbac import require_role

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

admin_only = Depends(require_role(RolEnum.admin))


@router.get("", response_model=List[UsuarioResponse], dependencies=[admin_only])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_only])
def crear_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario_in.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado."
        )

    nuevo_usuario = Usuario(
        nombre=usuario_in.nombre,
        email=usuario_in.email,
        password_hash=get_password_hash(usuario_in.password),
        rol=usuario_in.rol,
        activo=True
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.patch("/{usuario_id}/revocar", response_model=UsuarioResponse, dependencies=[admin_only])
def revocar_usuario(usuario_id: UUID, db: Session = Depends(get_db)):  # Cambiado a UUID
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )

    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario