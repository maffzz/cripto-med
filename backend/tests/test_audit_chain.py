"""
Pruebas de la cadena de logs inmutables (app/audit.py y audit_logs).
Estándares verificados:
- NIST SP 800-92 (Integridad de registros y detección de manipulaciones).
- OWASP Logging Cheat Sheet.
"""

from uuid import uuid4
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal, engine, Base
from app.models import AuditLog, Usuario, AccionEnum, RolEnum
from app.audit import log_action, calcular_hash_log, format_iso_utc, GENESIS_HASH


@pytest.fixture(scope="function")
def db_session(clean_audit_logs):
    """
    Crea tablas y sesión de BD para la prueba.
    Depende de clean_audit_logs (conftest) para limpiar audit_logs con permisos de owner.
    """
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Crea un usuario real en BD para cumplir la ForeignKey de audit_logs.usuario_id."""
    u = Usuario(
        id=uuid4(),
        nombre="Auditor de Pruebas",
        email=f"auditor_{uuid4().hex[:6]}@criptomed.local",
        password_hash="dummy_hash",
        rol=RolEnum.auditor,
        activo=True
    )
    db_session.add(u)
    db_session.commit()
    return u


def verificar_cadena_en_memoria(session: Session) -> tuple[bool, str]:
    """Función auxiliar que verifica la integridad de la cadena."""
    logs = session.query(AuditLog).order_by(AuditLog.seq.asc()).all()
    if not logs:
        return True, "Cadena vacía"

    hash_prev_esperado = GENESIS_HASH
    for log in logs:
        if log.hash_prev != hash_prev_esperado:
            return False, f"Falla encadenamiento en seq={log.seq}"

        ts_iso = format_iso_utc(log.timestamp)
        accion_str = log.accion.value if hasattr(log.accion, "value") else str(log.accion)

        recalc = calcular_hash_log(
            hash_prev=log.hash_prev,
            usuario_id=log.usuario_id,
            accion=accion_str,
            recurso=log.recurso,
            timestamp_iso=ts_iso,
            ip_origen=log.ip_origen,
            detalle=log.detalle
        )
        if log.hash_actual != recalc:
            return False, f"Falla integridad en seq={log.seq}"

        hash_prev_esperado = log.hash_actual

    return True, "Cadena íntegra"


def test_cadena_logs_cinco_eventos_integra(db_session, test_user):
    """Inserta 5 logs consecutivos (incluyendo uno con usuario_id=None) y verifica cadena 100% válida."""
    eventos = [
        (AccionEnum.login, "sistema:auth", test_user.id, "192.168.1.10", "Login exitoso"),
        (AccionEnum.lectura, "paciente:111", test_user.id, "192.168.1.10", "Consulta de historia"),
        (AccionEnum.edicion, "paciente:111", test_user.id, "192.168.1.10", "Actualización diagnóstico"),
        (AccionEnum.login, "sistema:auth", None, "192.168.1.99", "Intento login usuario inexistente"),
        (AccionEnum.transferencia, "paciente:111", test_user.id, "192.168.1.10", "Transferido a Dr. Quispe"),
    ]

    logs_insertados = []
    for accion, recurso, uid, ip, detalle in eventos:
        entry = log_action(
            db=db_session,
            accion=accion,
            recurso=recurso,
            usuario_id=uid,
            ip_origen=ip,
            detalle=detalle
        )
        logs_insertados.append(entry)

    assert len(logs_insertados) == 5

    # Validar que el primer registro tenga el hash génesis
    assert logs_insertados[0].hash_prev == GENESIS_HASH

    # Validar que cada log posterior enlace con el hash del anterior
    for i in range(1, 5):
        assert logs_insertados[i].hash_prev == logs_insertados[i - 1].hash_actual

    # Validar verificación forense
    valido, mensaje = verificar_cadena_en_memoria(db_session)
    assert valido is True
    assert mensaje == "Cadena íntegra"


def test_deteccion_alteracion_en_fila_intermedia(db_session, test_user, owner_engine):
    """Altera maliciosamente un registro intermedio desactivando triggers y valida que la verificación detecte la falla."""
    for i in range(5):
        log_action(
            db=db_session,
            accion=AccionEnum.lectura,
            recurso=f"paciente:uuid-{i}",
            usuario_id=test_user.id,
            ip_origen="10.0.0.1",
            detalle=f"Lectura número {i}"
        )

    valido_inicial, _ = verificar_cadena_en_memoria(db_session)
    assert valido_inicial is True

    # Alteramos el recurso de la fila intermedia desactivando el trigger temporalmente
    # usando el engine owner (requiere privilegios de superusuario/owner)
    from sqlalchemy.orm import sessionmaker as sm
    OSession = sm(bind=owner_engine)
    owner_sess = OSession()
    try:
        owner_sess.execute(text("ALTER TABLE audit_logs DISABLE TRIGGER ALL;"))
        owner_sess.commit()

        logs = owner_sess.query(AuditLog).order_by(AuditLog.seq.asc()).all()
        tercer_log = logs[2]
        tercer_seq = tercer_log.seq

        tercer_log.recurso = "paciente:uuid-ALTERADO-MALICIOSO"
        owner_sess.commit()

        owner_sess.execute(text("ALTER TABLE audit_logs ENABLE TRIGGER ALL;"))
        owner_sess.commit()
    finally:
        owner_sess.close()

    # Refrescar la sesión de test para ver el cambio
    db_session.expire_all()

    # La verificación forense debe detectar la rotura de integridad en la fila alterada
    valido_post_alteracion, mensaje_falla = verificar_cadena_en_memoria(db_session)
    assert valido_post_alteracion is False
    assert f"Falla integridad en seq={tercer_seq}" in mensaje_falla
