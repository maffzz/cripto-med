from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario, AuditLog, AccionEnum
from app.auth import verify_password, create_access_token, get_current_user
from app.schemas import Token, UsuarioResponse

# El prefijo '/auth' asegura que las rutas sean /auth/login y /auth/me
router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Valida credenciales y retorna el JWT."""
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    if not usuario or not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo."
        )

    access_token = create_access_token(data={"sub": usuario.email})
    
    # Registro de auditoría
    ip = request.client.host if request.client else "desconocida"
    log = AuditLog(
        usuario_id=usuario.id,
        accion=AccionEnum.login,
        recurso="sistema:auth",
        ip_origen=ip
    )
    db.add(log)
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """Retorna el usuario actual (requiere JWT)."""
    # Gracias a UsuarioResponse (en schemas.py), FastAPI excluye automáticamente 
    # la contraseña de la respuesta por seguridad.
    return current_user