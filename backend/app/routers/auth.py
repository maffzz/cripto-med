from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario, AccionEnum
from app.auth import verify_password, create_access_token, get_current_user
from app.audit import log_action, extract_client_ip
from app.schemas import Token, UsuarioResponse
from app.limiter import limiter

# Hash bcrypt precalculado (12 rondas) para igualar tiempos en usuarios inexistentes (OWASP / Anti-Timing)
DUMMY_BCRYPT_HASH = "$2b$12$uC5F7UkHePSNHaitOvBcdu0DdyXLjz0CeCdTPp94NegpXoGg1Hj5G"

# El prefijo '/auth' asegura que las rutas sean /auth/login y /auth/me
router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Valida credenciales y retorna el JWT.
    Aplica:
    - Rate limiting: 10 peticiones/minuto por IP.
    - Protección contra enumeración y timing attacks (tiempo constante para usuario inexistente).
    - Bloqueo temporal de 15 minutos tras 5 intentos fallidos consecutivos (NIST SP 800-63B).
    """
    ip = extract_client_ip(request)
    now = datetime.now(timezone.utc)
    
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    # 1. Mitigación contra enumeración de usuarios y Timing Attacks:
    # Si el usuario no existe, se calcula bcrypt contra el hash dummy para que el tiempo
    # de respuesta sea idéntico al de una contraseña errónea de un usuario real.
    if not usuario:
        verify_password(form_data.password, DUMMY_BCRYPT_HASH)
        log_action(
            db=db,
            accion=AccionEnum.login_fallido,
            recurso="sistema:auth",
            usuario_id=None,
            ip_origen=ip,
            detalle=f"Intento fallido (usuario inexistente): {form_data.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 2. Verificar si la cuenta se encuentra bloqueada
    bloqueado = usuario.bloqueado_hasta
    if bloqueado:
        if bloqueado.tzinfo is None:
            bloqueado = bloqueado.replace(tzinfo=timezone.utc)
        if bloqueado > now:
            log_action(
                db=db,
                accion=AccionEnum.login_fallido,
                recurso="sistema:auth",
                usuario_id=usuario.id,
                ip_origen=ip,
                detalle=f"Intento de acceso a cuenta bloqueada: {usuario.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Cuenta bloqueada temporalmente por múltiples intentos fallidos. Intente más tarde.",
            )
        else:
            # El período de 15 minutos ya expiró: desbloqueo automático
            usuario.intentos_fallidos = 0
            usuario.bloqueado_hasta = None
            db.commit()

    # 3. Verificar estado activo de la cuenta
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo."
        )

    # 4. Validar contraseña
    if not verify_password(form_data.password, usuario.password_hash):
        usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1
        
        if usuario.intentos_fallidos >= 5:
            # Umbral alcanzado: bloqueo de 15 minutos
            usuario.bloqueado_hasta = now + timedelta(minutes=15)
            db.commit()
            log_action(
                db=db,
                accion=AccionEnum.bloqueo,
                recurso="sistema:auth",
                usuario_id=usuario.id,
                ip_origen=ip,
                detalle=f"Cuenta bloqueada por 5 intentos fallidos consecutivos: {usuario.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Cuenta bloqueada temporalmente por múltiples intentos fallidos. Intente en 15 minutos.",
            )
        else:
            db.commit()
            log_action(
                db=db,
                accion=AccionEnum.login_fallido,
                recurso="sistema:auth",
                usuario_id=usuario.id,
                ip_origen=ip,
                detalle=f"Intento fallido ({usuario.intentos_fallidos}/5): {usuario.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # 5. Login exitoso: restablecer contadores y emitir JWT
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    db.commit()

    access_token = create_access_token(data={"sub": usuario.email})
    
    # Registro de auditoría encadenado con SHA-256
    log_action(
        db=db,
        accion=AccionEnum.login,
        recurso="sistema:auth",
        usuario_id=usuario.id,
        ip_origen=ip,
        detalle=f"Login exitoso: {usuario.email}"
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """Retorna el usuario actual (requiere JWT)."""
    # Gracias a UsuarioResponse (en schemas.py), FastAPI excluye automáticamente 
    # la contraseña de la respuesta por seguridad.
    return current_user
