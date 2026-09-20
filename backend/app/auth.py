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


# --- Funciones para Contraseñas ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash guardado."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Genera el hash seguro de una contraseña."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


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