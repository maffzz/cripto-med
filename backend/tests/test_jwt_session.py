"""
Pruebas de Seguridad para JWT y Gestión de Sesión (RFC 8725 / NIST SP 800-63B).
Estándares verificados:
- RFC 8725 Sección 3.1: Algoritmos permitidos (rechazo de 'none' y 'HS512').
- RFC 8725 Sección 3.3: Exigencia obligatoria de claims 'exp' y 'sub'.
- Revocación inmediata de sesión ante usuario inactivo (activo=False).
- Bloqueo inmediato de sesión ante cuenta suspendida (bloqueado_hasta).
- Expiración temporal estricta de tokens.
"""

import base64
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.main import app
from app.config import JWT_SECRET
from app.auth import create_access_token, get_password_hash
from app.database import SessionLocal, engine, Base
from app.models import Usuario, RolEnum


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user():
    """Crea un usuario para pruebas de sesión JWT."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    u = Usuario(
        id=uuid4(),
        nombre="Usuario Sesion Test",
        email=f"jwt_test_{uuid4().hex[:6]}@criptomed.com",
        password_hash=get_password_hash("PasswordValida2026!"),
        rol=RolEnum.doctor,
        activo=True,
        intentos_fallidos=0,
        bloqueado_hasta=None
    )
    session.add(u)
    session.commit()
    session.refresh(u)
    yield u
    session.close()


def test_token_valido_hs256_con_exp_y_sub_es_aceptado(client, test_user):
    """Verifica que un token legítimo con claims obligatorias y HS256 sea aceptado (200 OK)."""
    token = create_access_token(data={"sub": test_user.email})
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == test_user.email


def test_token_sin_exp_es_rechazado(client, test_user):
    """RFC 8725: Un token sin claim de expiración 'exp' debe ser rechazado (401)."""
    token_sin_exp = jwt.encode({"sub": test_user.email}, JWT_SECRET, algorithm="HS256")
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token_sin_exp}"})
    assert resp.status_code == 401


def test_token_sin_sub_es_rechazado(client):
    """RFC 8725: Un token sin claim 'sub' debe ser rechazado (401)."""
    exp = datetime.now(timezone.utc) + timedelta(minutes=15)
    token_sin_sub = jwt.encode({"exp": exp}, JWT_SECRET, algorithm="HS256")
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token_sin_sub}"})
    assert resp.status_code == 401


def test_token_con_algoritmo_none_rechazado(client, test_user):
    """RFC 8725: Tokens con alg 'none' (sin firma) deben ser tajantemente rechazados."""
    exp = int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp())
    header = _b64url_encode(json.dumps({"alg": "none", "typ": "JWT"}).encode("utf-8"))
    payload = _b64url_encode(json.dumps({"sub": test_user.email, "exp": exp}).encode("utf-8"))
    token_none = f"{header}.{payload}."
    
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token_none}"})
    assert resp.status_code == 401


def test_token_con_algoritmo_no_permitido_hs512_rechazado(client, test_user):
    """RFC 8725: Tokens firmados con algoritmos no permitidos (ej: HS512) deben ser rechazados."""
    exp = datetime.now(timezone.utc) + timedelta(minutes=15)
    token_hs512 = jwt.encode({"sub": test_user.email, "exp": exp}, JWT_SECRET, algorithm="HS512")
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token_hs512}"})
    assert resp.status_code == 401


def test_token_expirado_es_rechazado(client, test_user):
    """Tokens con 'exp' en el pasado deben ser rechazados inmediatamente (401)."""
    token_expirado = create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(seconds=-10)
    )
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token_expirado}"})
    assert resp.status_code == 401


def test_token_usuario_revocado_rechazado_inmediatamente(client, test_user):
    """Revocación inmediata: si activo=False en BD, el token es rechazado aunque sea válido en firma."""
    token = create_access_token(data={"sub": test_user.email})

    # Verificar que inicialmente funciona
    resp_ok = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_ok.status_code == 200

    # Desactivar/revocar usuario en la base de datos
    session = SessionLocal()
    u = session.query(Usuario).filter(Usuario.id == test_user.id).first()
    u.activo = False
    session.commit()
    session.close()

    # La siguiente petición protegida debe fallar de inmediato
    resp_revocado = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_revocado.status_code == 401
    assert "inactiva o revocada" in resp_revocado.json()["detail"].lower()


def test_token_usuario_bloqueado_rechazado_inmediatamente(client, test_user):
    """Bloqueo inmediato: si bloqueado_hasta > now en BD, la sesión queda denegada."""
    session = SessionLocal()
    u = session.query(Usuario).filter(Usuario.id == test_user.id).first()
    u.activo = True
    u.bloqueado_hasta = datetime.now(timezone.utc) + timedelta(minutes=15)
    session.commit()
    session.close()

    token = create_access_token(data={"sub": test_user.email})
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert "bloqueada" in resp.json()["detail"].lower()
