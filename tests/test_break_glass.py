"""
Pruebas de Acceso de Emergencia Break-Glass (Paso 1.8 - HIPAA 45 CFR 164.312 / NIST SP 800-92).
Estándares verificados:
- HIPAA 45 CFR § 164.312(a)(2)(ii): Procedimiento de acceso de emergencia documentado y verificable.
- Mínimo privilegio con escape de emergencia justificado (break-glass).
- Ventana temporal estricta de 30 minutos.
- Auditoría SHA-256 y alerta de seguridad para el auditor.
"""

from datetime import datetime, timedelta
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth import create_access_token, get_password_hash
from app.database import SessionLocal, engine, Base
from app.models import Usuario, Paciente, RolEnum, AuditLog, AccionEnum, AccesoEmergencia
from app.crypto import encrypt


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="function")
def emergency_data():
    """Configura un doctor asignado, un doctor de guardia no asignado, un auditor y un paciente."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # Doctor titular asignado
        doc_titular = Usuario(
            id=uuid4(),
            nombre="Dra. Titular Asignada",
            email=f"titular_{uuid4().hex[:6]}@criptomed.com",
            password_hash=get_password_hash("Password_Titular_2026!"),
            rol=RolEnum.doctor,
            activo=True,
        )
        # Doctor de urgencias (no asignado)
        doc_urgencias = Usuario(
            id=uuid4(),
            nombre="Dr. Urgencias Guardia",
            email=f"urgencias_{uuid4().hex[:6]}@criptomed.com",
            password_hash=get_password_hash("Password_Urgencias_2026!"),
            rol=RolEnum.doctor,
            activo=True,
        )
        # Auditor
        auditor = Usuario(
            id=uuid4(),
            nombre="Auditor Clinico",
            email=f"auditor_{uuid4().hex[:6]}@criptomed.com",
            password_hash=get_password_hash("Password_Auditor_2026!"),
            rol=RolEnum.auditor,
            activo=True,
        )
        # Personal Administrativo
        adminis = Usuario(
            id=uuid4(),
            nombre="Personal Mesa Entrada",
            email=f"adminis_{uuid4().hex[:6]}@criptomed.com",
            password_hash=get_password_hash("Password_Adminis_2026!"),
            rol=RolEnum.administrativo,
            activo=True,
        )
        # Paciente titular
        user_pac = Usuario(
            id=uuid4(),
            nombre="Paciente Critico Demo",
            email=f"pac_crit_{uuid4().hex[:6]}@criptomed.com",
            password_hash=get_password_hash("Password_PacCrit_2026!"),
            rol=RolEnum.paciente,
            activo=True,
        )
        session.add_all([doc_titular, doc_urgencias, auditor, adminis, user_pac])
        session.commit()

        pid = uuid4()
        pid_str = str(pid)
        paciente = Paciente(
            id=pid,
            usuario_id=user_pac.id,
            doctor_id=doc_titular.id,
            nombre=encrypt("Paciente Critico Demo", aad=f"pacientes.nombre.{pid_str}"),
            edad=52,
            genero="Masculino",
            tipo_sangre="O-",
            diagnostico=encrypt("Choque anafiláctico grave", aad=f"pacientes.diagnostico.{pid_str}"),
            codigo_cie10="I10",
            fecha_admision=datetime.utcnow() - timedelta(days=1),
            hospital="Hospital Emergencias Grau",
            proveedor_seguro="EsSalud",
            monto_facturado=encrypt("2400.00", aad=f"pacientes.monto_facturado.{pid_str}"),
            numero_habitacion="UCI-04",
            tipo_admision="Emergencia Shock Trauma",
            medicacion=encrypt("Adrenalina 0.5mg IM + Hidrocortisona", aad=f"pacientes.medicacion.{pid_str}"),
            resultado_test=encrypt("Saturación 88%, hipotensión severa", aad=f"pacientes.resultado_test.{pid_str}"),
            consentimiento_fecha=datetime.utcnow() - timedelta(days=1),
            consentimiento_version="v1.0",
        )
        session.add(paciente)
        session.commit()

        yield {
            "doc_titular": doc_titular,
            "doc_urgencias": doc_urgencias,
            "auditor": auditor,
            "adminis": adminis,
            "user_pac": user_pac,
            "paciente": paciente,
            "tokens": {
                "doc_titular": create_access_token({"sub": doc_titular.email}),
                "doc_urgencias": create_access_token({"sub": doc_urgencias.email}),
                "auditor": create_access_token({"sub": auditor.email}),
                "adminis": create_access_token({"sub": adminis.email}),
                "paciente": create_access_token({"sub": user_pac.email}),
            }
        }
    finally:
        session.close()


def test_rol_no_doctor_rechazado_para_acceso_emergencia(client, emergency_data):
    """Verifica que solo usuarios con rol doctor puedan invocar break-glass (HTTP 403)."""
    headers_adminis = {"Authorization": f"Bearer {emergency_data['tokens']['adminis']}"}
    pid = emergency_data["paciente"].id
    body = {"justificacion": "Paciente inconsciente requiere atención inmediata en shock trauma"}

    resp = client.post(f"/pacientes/{pid}/acceso-emergencia", json=body, headers=headers_adminis)
    assert resp.status_code == 403
    assert "exclusivo para personal médico" in resp.json()["detail"]


def test_justificacion_menor_20_caracteres_rechazada(client, emergency_data):
    """Verifica que se exija una justificación médica descriptiva de al menos 20 caracteres."""
    headers_urg = {"Authorization": f"Bearer {emergency_data['tokens']['doc_urgencias']}"}
    pid = emergency_data["paciente"].id
    body = {"justificacion": "Urgencia médica"}  # 15 caracteres

    resp = client.post(f"/pacientes/{pid}/acceso-emergencia", json=body, headers=headers_urg)
    assert resp.status_code == 400
    assert "al menos 20 caracteres" in resp.json()["detail"]


def test_doctor_obtiene_acceso_emergencia_y_desbloquea_lectura_por_30_min(client, emergency_data):
    """Verifica que el doctor no asignado active el break-glass y luego consulte el expediente."""
    headers_urg = {"Authorization": f"Bearer {emergency_data['tokens']['doc_urgencias']}"}
    pid = emergency_data["paciente"].id

    # 1. Antes del break-glass: Doctor de urgencias recibe HTTP 403
    resp_pre = client.get(f"/pacientes/{pid}", headers=headers_urg)
    assert resp_pre.status_code == 403

    # 2. Invocación de break-glass con justificación médica válida
    justif = "Paciente en shock anafiláctico en trauma shock; requiere verificar antecedentes alérgicos urgentes"
    resp_bg = client.post(
        f"/pacientes/{pid}/acceso-emergencia",
        json={"justificacion": justif},
        headers=headers_urg
    )
    assert resp_bg.status_code == 200
    data_bg = resp_bg.json()
    assert "concedido por 30 minutos" in data_bg["mensaje"]
    assert data_bg["paciente"]["diagnostico_descifrado"] == "Choque anafiláctico grave"
    assert data_bg["paciente"]["medicacion_descifrado"] == "Adrenalina 0.5mg IM + Hidrocortisona"

    # 3. Durante la ventana de 30 minutos: GET /pacientes/{id} responde HTTP 200
    resp_post = client.get(f"/pacientes/{pid}", headers=headers_urg)
    assert resp_post.status_code == 200
    assert resp_post.json()["nombre_descifrado"] == "Paciente Critico Demo"


def test_acceso_emergencia_expirado_vuelve_a_restringir_acceso(client, emergency_data):
    """Verifica que al vencer la ventana de 30 minutos el acceso vuelva a retornar 403."""
    headers_urg = {"Authorization": f"Bearer {emergency_data['tokens']['doc_urgencias']}"}
    pid = emergency_data["paciente"].id

    # Crear acceso con expira_en en el pasado
    session = SessionLocal()
    try:
        acceso_vencido = AccesoEmergencia(
            id=uuid4(),
            paciente_id=pid,
            doctor_id=emergency_data["doc_urgencias"].id,
            justificacion="Atención de emergencia finalizada hace más de 30 minutos",
            otorgado_en=datetime.utcnow() - timedelta(minutes=40),
            expira_en=datetime.utcnow() - timedelta(minutes=10),
        )
        session.add(acceso_vencido)
        session.commit()
    finally:
        session.close()

    # Intento de lectura con pase expirado: debe ser 403
    resp = client.get(f"/pacientes/{pid}", headers=headers_urg)
    assert resp.status_code == 403
    assert "No autorizado" in resp.json()["detail"]


def test_acceso_emergencia_figura_en_alertas_de_auditor_y_en_historial_paciente(client, emergency_data):
    """Verifica que el evento de break-glass alerte al auditor y se notifique al paciente."""
    headers_urg = {"Authorization": f"Bearer {emergency_data['tokens']['doc_urgencias']}"}
    headers_aud = {"Authorization": f"Bearer {emergency_data['tokens']['auditor']}"}
    headers_pac = {"Authorization": f"Bearer {emergency_data['tokens']['paciente']}"}
    pid = emergency_data["paciente"].id

    # 1. Ejecutar break-glass
    justif = "Paciente inconsciente con traumatismo craneoencefálico sin datos de familiares"
    resp_bg = client.post(
        f"/pacientes/{pid}/acceso-emergencia",
        json={"justificacion": justif},
        headers=headers_urg
    )
    assert resp_bg.status_code == 200

    # 2. Auditor consulta GET /audit-logs/alertas
    resp_alertas = client.get("/audit-logs/alertas", headers=headers_aud)
    assert resp_alertas.status_code == 200
    alertas = resp_alertas.json()["alertas"]
    alertas_bg = [a for a in alertas if a["tipo"] == "ACCESO_EMERGENCIA_BREAK_GLASS"]
    assert len(alertas_bg) >= 1
    assert any(f"paciente:{pid}" in a["recurso"] for a in alertas_bg)

    # 3. Paciente consulta GET /pacientes/me/accesos
    resp_pac_accesos = client.get("/pacientes/me/accesos", headers=headers_pac)
    assert resp_pac_accesos.status_code == 200
    items = resp_pac_accesos.json()["items"]
    items_bg = [it for it in items if it["accion"] == "acceso_emergencia"]
    assert len(items_bg) >= 1
    assert "Dr. Urgencias Guardia" in items_bg[0]["profesional_nombre"]
    assert justif in items_bg[0]["detalle"]
