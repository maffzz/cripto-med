"""
Pruebas de Bloqueo por intentos fallidos, Anti-Timing, Rate Limiting y Alertas.
Estándares verificados:
- NIST SP 800-63B (Control de autenticación, bloqueo tras intentos fallidos).
- OWASP Authentication & Timing Attacks Cheat Sheet.
- NIST SP 800-61 / 800-92 (Detección de anomalías y alertas forenses).
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.database import SessionLocal, engine, Base
from app.models import Usuario, AuditLog, RolEnum, AccionEnum
from app.auth import get_password_hash, create_access_token
from app.audit import log_action


@pytest.fixture(scope="function")
def db_session():
    """Fixture de base de datos con limpieza de registros de prueba."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    # Limpiar logs y usuarios previos de prueba
    try:
        session.execute(text("ALTER TABLE audit_logs DISABLE TRIGGER ALL;"))
        session.commit()
    except Exception:
        pass

    session.query(AuditLog).delete()
    session.query(Usuario).filter(Usuario.email.like("%@testbloqueo.local")).delete()
    session.commit()

    try:
        session.execute(text("ALTER TABLE audit_logs ENABLE TRIGGER ALL;"))
        session.commit()
    except Exception:
        pass

    yield session

    # Teardown
    try:
        session.execute(text("ALTER TABLE audit_logs DISABLE TRIGGER ALL;"))
        session.commit()
        session.query(AuditLog).delete()
        session.query(Usuario).filter(Usuario.email.like("%@testbloqueo.local")).delete()
        session.commit()
        session.execute(text("ALTER TABLE audit_logs ENABLE TRIGGER ALL;"))
        session.commit()
    except Exception:
        pass

    session.close()


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


@pytest.fixture(scope="function")
def user_bloqueo(db_session):
    """Crea un usuario para pruebas de bloqueo."""
    u = Usuario(
        id=uuid4(),
        nombre="Usuario Prueba Bloqueo",
        email="victima@testbloqueo.local",
        password_hash=get_password_hash("Password123!"),
        rol=RolEnum.doctor,
        activo=True,
        intentos_fallidos=0,
        bloqueado_hasta=None
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def admin_user(db_session):
    """Crea un administrador para consultar alertas."""
    u = Usuario(
        id=uuid4(),
        nombre="Admin Alertas",
        email="admin@testbloqueo.local",
        password_hash=get_password_hash("AdminPass123!"),
        rol=RolEnum.admin,
        activo=True
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def test_login_exitoso_y_reinicio_contador(client, db_session, user_bloqueo):
    """Verifica que un login exitoso resetee intentos fallidos y bloqueado_hasta."""
    user_bloqueo.intentos_fallidos = 3
    db_session.commit()

    response = client.post("/auth/login", data={
        "username": "victima@testbloqueo.local",
        "password": "Password123!"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

    db_session.refresh(user_bloqueo)
    assert user_bloqueo.intentos_fallidos == 0
    assert user_bloqueo.bloqueado_hasta is None


def test_login_usuario_inexistente_retorna_401_identico(client, db_session):
    """Verifica respuesta idéntica y registro de log ante usuario inexistente (OWASP Anti-Enumeración)."""
    response = client.post("/auth/login", data={
        "username": "inexistente@testbloqueo.local",
        "password": "CualquierPassword123"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos"

    # Verificar que se registró log con usuario_id None
    log = db_session.query(AuditLog).filter(
        AuditLog.accion == AccionEnum.login_fallido,
        AuditLog.usuario_id.is_(None)
    ).first()
    assert log is not None
    assert "inexistente@testbloqueo.local" in log.detalle


def test_bloqueo_al_quinto_intento_fallido(client, db_session, user_bloqueo):
    """Verifica bloqueo temporal tras 5 intentos fallidos consecutivos (NIST SP 800-63B)."""
    # Intentos 1 a 4: retornan 401 Unauthorized
    for i in range(1, 5):
        resp = client.post("/auth/login", data={
            "username": user_bloqueo.email,
            "password": "WrongPassword!"
        })
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Correo o contraseña incorrectos"

    # Intento 5: debe bloquear la cuenta y retornar 429 Too Many Requests
    resp5 = client.post("/auth/login", data={
        "username": user_bloqueo.email,
        "password": "WrongPassword!"
    })
    assert resp5.status_code == 429
    assert "bloqueada" in resp5.json()["detail"].lower()

    db_session.refresh(user_bloqueo)
    assert user_bloqueo.intentos_fallidos >= 5
    assert user_bloqueo.bloqueado_hasta is not None

    # Verificar registro de evento bloqueo en auditoría
    log_bloqueo = db_session.query(AuditLog).filter(
        AuditLog.usuario_id == user_bloqueo.id,
        AuditLog.accion == AccionEnum.bloqueo
    ).first()
    assert log_bloqueo is not None


def test_intento_en_cuenta_bloqueada_retorna_429(client, db_session, user_bloqueo):
    """Verifica que no se permita login mientras la cuenta esté dentro del tiempo de bloqueo."""
    user_bloqueo.bloqueado_hasta = datetime.now(timezone.utc) + timedelta(minutes=10)
    user_bloqueo.intentos_fallidos = 5
    db_session.commit()

    # Incluso con la contraseña correcta debe rechazar con 429
    resp = client.post("/auth/login", data={
        "username": user_bloqueo.email,
        "password": "Password123!"
    })
    assert resp.status_code == 429
    assert "bloqueada" in resp.json()["detail"].lower()


def test_desbloqueo_automatico_tras_expiracion(client, db_session, user_bloqueo):
    """Verifica que al vencer el plazo de 15 minutos la cuenta vuelva a permitir acceso."""
    user_bloqueo.bloqueado_hasta = datetime.now(timezone.utc) - timedelta(minutes=1)
    user_bloqueo.intentos_fallidos = 5
    db_session.commit()

    resp = client.post("/auth/login", data={
        "username": user_bloqueo.email,
        "password": "Password123!"
    })
    assert resp.status_code == 200

    db_session.refresh(user_bloqueo)
    assert user_bloqueo.intentos_fallidos == 0
    assert user_bloqueo.bloqueado_hasta is None


def test_alertas_fuerza_bruta_y_horario_y_volumen(client, db_session, admin_user, user_bloqueo):
    """Verifica la detección de las 3 anomalías en GET /audit-logs/alertas."""
    now = datetime.now(timezone.utc)
    token_admin = create_access_token(data={"sub": admin_user.email})
    headers = {"Authorization": f"Bearer {token_admin}"}

    # 1. Simular 5 intentos fallidos en los últimos 5 minutos para user_bloqueo
    for i in range(5):
        log_action(
            db=db_session,
            accion=AccionEnum.login_fallido,
            recurso="sistema:auth",
            usuario_id=user_bloqueo.id,
            ip_origen="192.168.1.50",
            detalle=f"Fallo #{i+1}"
        )

    # 2. Simular lectura fuera de horario laboral (ej: 23:00 hora de Lima -> 04:00 UTC)
    # Creamos un log con timestamp de hace 2 horas pero hora local 23:30 (Lima UTC-5)
    # Por ejemplo: hoy a las 04:30 UTC
    ts_nocturno = datetime(now.year, now.month, now.day, 4, 30, 0, tzinfo=timezone.utc)
    log_fuera_horario = AuditLog(
        usuario_id=user_bloqueo.id,
        accion=AccionEnum.lectura,
        recurso="paciente:historia-nocturna",
        ip_origen="192.168.1.99",
        timestamp=ts_nocturno,
        hash_prev="0"*64,
        hash_actual="dummy_hash"
    )
    db_session.add(log_fuera_horario)
    db_session.commit()

    # 3. Simular volumen anómalo: 35 lecturas distintas en la última hora
    for i in range(35):
        log_action(
            db=db_session,
            accion=AccionEnum.lectura,
            recurso=f"paciente:uuid-{i}",
            usuario_id=user_bloqueo.id,
            ip_origen="10.0.0.1",
            detalle=f"Consulta masiva #{i}"
        )

    # Consultar alertas
    resp = client.get("/audit-logs/alertas?umbral_lecturas=30", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    tipos_alertas = [a["tipo"] for a in data["alertas"]]
    assert "FUERZA_BRUTA_LOGIN" in tipos_alertas
    assert "ACCESO_FUERA_DE_HORARIO" in tipos_alertas
    assert "VOLUMEN_ANOMALO_LECTURAS" in tipos_alertas


def test_alertas_restringido_a_admin_auditor(client, db_session, user_bloqueo):
    """Verifica que un usuario con rol médico no pueda consultar el endpoint de alertas (403 Forbidden)."""
    token_doctor = create_access_token(data={"sub": user_bloqueo.email})
    headers = {"Authorization": f"Bearer {token_doctor}"}

    resp = client.get("/audit-logs/alertas", headers=headers)
    assert resp.status_code == 403


def test_rate_limiting_slowapi(client, user_bloqueo):
    """Verifica que slowapi bloquee con 429 al exceder 10 peticiones/minuto por IP."""
    from app.limiter import limiter
    limiter.enabled = True
    try:
        respuestas = []
        for _ in range(12):
            r = client.post("/auth/login", data={
                "username": user_bloqueo.email,
                "password": "Password123!"
            }, headers={"X-Forwarded-For": "203.0.113.88"})
            respuestas.append(r.status_code)
        assert 429 in respuestas
    finally:
        limiter.enabled = False

