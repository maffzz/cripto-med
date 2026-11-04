"""
Pruebas de la Política de Contraseñas alineada a NIST SP 800-63B.
Estándares verificados:
- NIST SP 800-63B Sección 5.1.1.2 (Memorized Secret Verifiers).
- Longitud mínima de 12 caracteres, límite de 72 bytes de bcrypt.
- Sin reglas forzadas de composición (sin exigir mayúsculas/símbolos).
- Rechazo de contraseñas débiles/comunes mediante zxcvbn (puntaje >= 3).
- Rechazo de contraseñas que contienen el nombre o correo del usuario.
- Factor de costo de bcrypt verificado en 12 rondas ($2b$12$).
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.auth import validate_password_policy, get_password_hash, create_access_token
from app.database import SessionLocal, engine, Base
from app.models import Usuario, RolEnum


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def admin_token():
    """Crea token de administrador para probar POST /usuarios."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    admin = session.query(Usuario).filter(Usuario.rol == RolEnum.admin).first()
    if not admin:
        admin = Usuario(
            id=uuid4(),
            nombre="Admin Test Policy",
            email="admin_policy@test.local",
            password_hash=get_password_hash("AdminPassPolicy2026!"),
            rol=RolEnum.admin,
            activo=True
        )
        session.add(admin)
        session.commit()
    email = admin.email
    session.close()
    return create_access_token(data={"sub": email})


# ------------------------------------------------------------------------------
# 1. Pruebas Unitarias de validate_password_policy
# ------------------------------------------------------------------------------

def test_password_valida_pasa_exitosamente():
    """Una contraseña >= 12 caracteres con buena entropía es aceptada."""
    # NIST SP 800-63B: frases de paso sin símbolos también deben ser permitidas si tienen suficiente entropía
    password_valida = "orquidea purpura florece temprano"
    validate_password_policy(password_valida, email="dr.soto@criptomed.com", nombre="Carlos Soto")


def test_password_corta_menor_12_rechazada():
    """Contraseñas con menos de 12 caracteres deben ser rechazadas."""
    with pytest.raises(ValueError, match="al menos 12 caracteres"):
        validate_password_policy("Clave123!", email="test@criptomed.com", nombre="Juan Perez")


def test_password_mayor_72_bytes_rechazada_sin_truncar():
    """Contraseñas que exceden el límite de 72 bytes de bcrypt deben ser rechazadas explícitamente."""
    password_larga_73_bytes = "A" * 73
    with pytest.raises(ValueError, match="72 bytes"):
        validate_password_policy(password_larga_73_bytes)

    # Caracteres multibyte UTF-8 (ej: acentos o emojis)
    # Cada emoji puede medir 4 bytes en UTF-8
    emoji_pwd = "🔒" * 19  # 19 * 4 = 76 bytes (> 72 bytes)
    with pytest.raises(ValueError, match="72 bytes"):
        validate_password_policy(emoji_pwd)


def test_password_con_email_usuario_rechazada():
    """Contraseña que contiene partes del correo electrónico es rechazada."""
    with pytest.raises(ValueError, match="correo electrónico"):
        validate_password_policy("SuperClaveSegura_ana.garcia_2026", email="ana.garcia@hospital.org", nombre="Ana Gomez")


def test_password_con_nombre_usuario_rechazada():
    """Contraseña que contiene fragmentos del nombre del usuario es rechazada."""
    with pytest.raises(ValueError, match="nombre o apellidos"):
        validate_password_policy("ClaveSecreta_Rodriguez_2026", email="usuario@hospital.org", nombre="Ernesto Rodriguez")


def test_password_comun_debil_rechazada_por_zxcvbn():
    """Contraseñas predecibles o comunes con zxcvbn score < 3 son rechazadas."""
    passwords_debiles = [
        "password123456",
        "qwertyuiopasdfgh",
        "1234567890123456",
        "administrator123"
    ]
    for debil in passwords_debiles:
        with pytest.raises(ValueError, match="NIST SP 800-63B|zxcvbn"):
            validate_password_policy(debil, email="seguro@test.local", nombre="Prueba")


def test_factor_de_costo_bcrypt_es_12():
    """Verifica que el hash generado por get_password_hash tenga rounds=12 ($2b$12$)."""
    hash_generado = get_password_hash("ContrasenaSegura2026!")
    assert hash_generado.startswith("$2b$12$")


# ------------------------------------------------------------------------------
# 2. Pruebas de Integración en Endpoints (POST /usuarios)
# ------------------------------------------------------------------------------

def test_endpoint_crear_usuario_rechaza_password_invalida(client, admin_token):
    """POST /usuarios retorna HTTP 400 Bad Request si la contraseña no cumple la política NIST."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "email": f"nuevo_{uuid4().hex[:6]}@criptomed.com",
        "nombre": "Roberto Martinez",
        "password": "corta",  # Inválida (<12 chars)
        "rol": "doctor"
    }
    resp = client.post("/usuarios", json=payload, headers=headers)
    assert resp.status_code == 400
    assert "al menos 12 caracteres" in resp.json()["detail"]


def test_endpoint_crear_usuario_acepta_password_valida(client, admin_token):
    """POST /usuarios retorna HTTP 201 Created cuando la contraseña cumple con NIST SP 800-63B."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "email": f"nuevo_{uuid4().hex[:6]}@criptomed.com",
        "nombre": "Beatriz Morales",
        "password": "Nebulosa_Brillante_2026!",
        "rol": "doctor"
    }
    resp = client.post("/usuarios", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == payload["email"]
    assert "password" not in data
