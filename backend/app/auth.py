from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from app.database import get_db
from app.models import Usuario

# Esquema OAuth2 indicando el endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# --- Funciones para Contraseñas (NIST SP 800-63B) ---

def validate_password_policy(password: str, email: str = "", nombre: str = "") -> None:
    """
    Valida la política de contraseñas alineada con NIST SP 800-63B:
    1. Longitud mínima de 12 caracteres.
    2. Longitud máxima de 72 bytes en UTF-8 (límite nativo de bcrypt; se rechaza explícitamente).
    3. Sin reglas de composición obligatorias (no exige mayúsculas/símbolos) y sin caducidad forzada.
    4. Rechaza contraseñas que contengan el correo o nombre del usuario.
    5. Evaluación de entropía con zxcvbn (puntuación mínima 3/4).
    """
    if not password:
        raise ValueError("La contraseña no puede estar vacía.")

    # 1. Longitud mínima de 12 caracteres
    if len(password) < 12:
        raise ValueError("La contraseña debe tener al menos 12 caracteres (NIST SP 800-63B).")

    # 2. Longitud máxima de 72 bytes en UTF-8 (límite de bcrypt)
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("La contraseña excede el límite de 72 bytes de bcrypt. Por favor elija una longitud menor.")

    # 3. Rechazar datos personales del usuario (email o nombre)
    if email:
        email_clean = email.lower().strip()
        usuario_email = email_clean.split("@")[0]
        if len(usuario_email) >= 3 and usuario_email in password.lower():
            raise ValueError("La contraseña no debe contener su nombre de usuario o correo electrónico.")
        if email_clean in password.lower():
            raise ValueError("La contraseña no debe contener su dirección de correo electrónico.")

    if nombre:
        nombre_clean = nombre.lower().strip()
        for token in nombre_clean.split():
            if len(token) >= 3 and token in password.lower():
                raise ValueError("La contraseña no debe contener su nombre o apellidos.")

    # 4. Evaluación de entropía y diccionario de contraseñas comunes con zxcvbn
    import zxcvbn
    user_inputs = []
    if email:
        user_inputs.extend(email.lower().split("@"))
    if nombre:
        user_inputs.extend(nombre.lower().split())

    res = zxcvbn.zxcvbn(password, user_inputs=user_inputs)
    if res["score"] < 3:
        feedback = res.get("feedback", {})
        warning = feedback.get("warning") or "La contraseña es muy común o predecible"
        raise ValueError(f"Contraseña débil según NIST SP 800-63B (puntaje {res['score']}/4). {warning}.")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash guardado."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Genera el hash seguro de una contraseña con factor de costo 12 (NIST SP 800-63B)."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


# --- Funciones para JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un token JWT firmado con expiración."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(JWT_EXPIRE_MINUTES))
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# --- Dependencia de Autenticación de Endpoints ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """Valida el token Bearer y retorna el usuario autenticado actual."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de acceso.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifica el token usando la clave secreta y algoritmo configurado
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Busca al usuario en la base de datos
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise credentials_exception
        
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usuario inactivo en el sistema."
        )
        
    return user