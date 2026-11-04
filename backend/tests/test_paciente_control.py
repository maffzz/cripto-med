"""
Pruebas de Control y Transparencia para el Paciente (Paso 1.7 - Ley 29733 / NIST SP 800-92).
Estándares verificados:
- Ley 29733 (Protección de Datos Personales de Perú): Derechos de Acceso y Portabilidad.
- NIST SP 800-92: Registro inmutable de auditoría para accesos y exportación.
- OWASP ASVS: Control de acceso basado en roles y aislamiento estricto entre titulares.
"""

from datetime import datetime, timedelta
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth import create_access_token, get_password_hash
from app.database import SessionLocal, engine, Base
from app.models import Usuario, Paciente, RolEnum, AuditLog, AccionEnum
from app.crypto import encrypt, decrypt


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="function")
def data(client):
    """Crea doctores y pacientes para verificar control, trazabilidad y transferencia."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # Doctor 1
        doc1 = Usuario(
            id=uuid4(),
            nombre="Dra. Primera Medico",
            email=f"doc1_{uuid4().hex[:6]}@criptomed.com",
            password_hash=get_password_hash("Password_Doc1_2026!"),
            rol=RolEnum.doctor,
            activo=True,
        )
        # Doctor 2
        doc2 = Usuario(
            id=uuid4(),
            nombre="Dr. Segundo Medico",
            email=f"doc2_{uuid4().hex[:6]}@criptomed.com",
            password_hash=get_password_hash("Password_Doc2_2026!"),
            rol=RolEnum.doctor,
            activo=True,
        )
        # Paciente A (titular)
        user_pac_a = Usuario(
            id=uuid4(),
            nombre="Paciente Titular A",
            email=f"pac_a_{uuid4().hex[:6]}@criptomed.com",
            password_hash=get_password_hash("Password_PacA_2026!"),
            rol=RolEnum.paciente,
            activo=True,
        )
        # Paciente B (otro titular)
        user_pac_b = Usuario(
            id=uuid4(),
            nombre="Paciente Titular B",
            email=f"pac_b_{uuid4().hex[:6]}@criptomed.com",
            password_hash=get_password_hash("Password_PacB_2026!"),
            rol=RolEnum.paciente,
            activo=True,
        )
        session.add_all([doc1, doc2, user_pac_a, user_pac_b])
        session.commit()

        # Expediente Paciente A (asignado a Doctor 1)
        pid_a = uuid4()
        pid_a_str = str(pid_a)
        pac_a = Paciente(
            id=pid_a,
            usuario_id=user_pac_a.id,
            doctor_id=doc1.id,
            nombre=encrypt("Paciente Titular A", aad=f"pacientes.nombre.{pid_a_str}"),
            edad=29,
            genero="Femenino",
            tipo_sangre="A+",
            diagnostico=encrypt("Diagnóstico Confidencial A", aad=f"pacientes.diagnostico.{pid_a_str}"),
            codigo_cie10="I10",
            fecha_admision=datetime.utcnow() - timedelta(days=5),
            hospital="Hospital Santa Rosa",
            proveedor_seguro="Rímac EPS",
            monto_facturado=encrypt("750.00", aad=f"pacientes.monto_facturado.{pid_a_str}"),
            numero_habitacion="201",
            tipo_admision="Ambulatoria",
            medicacion=encrypt("Aspirina 100mg", aad=f"pacientes.medicacion.{pid_a_str}"),
            resultado_test=encrypt("Normal", aad=f"pacientes.resultado_test.{pid_a_str}"),
            consentimiento_fecha=datetime.utcnow() - timedelta(days=5),
            consentimiento_version="v1.0"
        )

        # Expediente Paciente B (asignado a Doctor 2)
        pid_b = uuid4()
        pid_b_str = str(pid_b)
        pac_b = Paciente(
            id=pid_b,
            usuario_id=user_pac_b.id,
            doctor_id=doc2.id,
            nombre=encrypt("Paciente Titular B", aad=f"pacientes.nombre.{pid_b_str}"),
            edad=45,
            genero="Masculino",
            tipo_sangre="O+",
            diagnostico=encrypt("Diagnóstico Confidencial B", aad=f"pacientes.diagnostico.{pid_b_str}"),
            codigo_cie10="E11",
            fecha_admision=datetime.utcnow() - timedelta(days=2),
            hospital="Hospital Santa Rosa",
            proveedor_seguro="Pacífico EPS",
            monto_facturado=encrypt("1200.00", aad=f"pacientes.monto_facturado.{pid_b_str}"),
            numero_habitacion="202",
            tipo_admision="Urgencia",
            medicacion=encrypt("Metformina 850mg", aad=f"pacientes.medicacion.{pid_b_str}"),
            resultado_test=encrypt("Glucosa 140", aad=f"pacientes.resultado_test.{pid_b_str}"),
            consentimiento_fecha=datetime.utcnow() - timedelta(days=2),
            consentimiento_version="v1.0"
        )
        session.add_all([pac_a, pac_b])
        session.commit()

        yield {
            "doc1": doc1,
            "doc2": doc2,
            "user_pac_a": user_pac_a,
            "user_pac_b": user_pac_b,
            "pac_a": pac_a,
            "pac_b": pac_b,
            "tokens": {
                "doc1": create_access_token({"sub": doc1.email}),
                "doc2": create_access_token({"sub": doc2.email}),
                "pac_a": create_access_token({"sub": user_pac_a.email}),
                "pac_b": create_access_token({"sub": user_pac_b.email}),
            }
        }
    finally:
        session.close()


def test_paciente_puede_ver_su_propio_historial_y_consentimiento(client, data):
    """Verifica que el titular consulte exitosamente su propio expediente con consentimiento."""
    headers = {"Authorization": f"Bearer {data['tokens']['pac_a']}"}
    resp = client.get("/pacientes/me", headers=headers)
    assert resp.status_code == 200
    res = resp.json()
    assert res["id"] == str(data["pac_a"].id)
    assert res["nombre_descifrado"] == "Paciente Titular A"
    assert res["diagnostico_descifrado"] == "Diagnóstico Confidencial A"
    assert res["consentimiento_version"] == "v1.0"
    assert res["consentimiento_fecha"] is not None


def test_rol_no_paciente_rechazado_en_endpoints_me(client, data):
    """Verifica que usuarios con rol doctor u otros no puedan invocar /pacientes/me (HTTP 403)."""
    headers = {"Authorization": f"Bearer {data['tokens']['doc1']}"}
    
    resp_me = client.get("/pacientes/me", headers=headers)
    assert resp_me.status_code == 403

    resp_accesos = client.get("/pacientes/me/accesos", headers=headers)
    assert resp_accesos.status_code == 403

    resp_export = client.get("/pacientes/me/export", headers=headers)
    assert resp_export.status_code == 403


def test_paciente_ve_accesos_a_su_historial_paginados(client, data):
    """Verifica que el paciente consulte los accesos a su expediente (NIST SP 800-92)."""
    # 1. El Doctor 1 consulta el expediente del Paciente A
    headers_doc1 = {"Authorization": f"Bearer {data['tokens']['doc1']}"}
    resp_doc = client.get(f"/pacientes/{data['pac_a'].id}", headers=headers_doc1)
    assert resp_doc.status_code == 200

    # 2. El Paciente A consulta su lista de accesos
    headers_pac = {"Authorization": f"Bearer {data['tokens']['pac_a']}"}
    resp_accesos = client.get("/pacientes/me/accesos", headers=headers_pac)
    assert resp_accesos.status_code == 200
    res = resp_accesos.json()
    assert "items" in res
    assert res["total"] >= 1
    
    # Debe aparecer el acceso del Doctor 1
    accesos_doc = [item for item in res["items"] if item["profesional_rol"] == "doctor"]
    assert len(accesos_doc) >= 1
    assert accesos_doc[0]["accion"] == "lectura"
    assert "Dra. Primera Medico" in accesos_doc[0]["profesional_nombre"]


def test_paciente_exporta_sus_datos_y_registra_evento_exportacion(client, data):
    """Verifica que el titular ejerza su derecho de acceso/portabilidad y registre exportacion."""
    headers_pac = {"Authorization": f"Bearer {data['tokens']['pac_a']}"}
    resp = client.get("/pacientes/me/export", headers=headers_pac)
    assert resp.status_code == 200
    res = resp.json()
    
    # Validar estructura y datos descifrados
    assert "titular" in res
    assert "expediente" in res
    assert "metadatos_exportacion" in res
    assert res["expediente"]["nombre"] == "Paciente Titular A"
    assert res["expediente"]["diagnostico"] == "Diagnóstico Confidencial A"
    assert res["expediente"]["consentimiento"]["version"] == "v1.0"

    # Verificar que el evento 'exportacion' quedó registrado en audit_logs
    session = SessionLocal()
    try:
        log = (
            session.query(AuditLog)
            .filter(
                AuditLog.recurso == f"paciente:{data['pac_a'].id}",
                AuditLog.accion == AccionEnum.exportacion
            )
            .order_by(AuditLog.seq.desc())
            .first()
        )
        assert log is not None
        assert log.usuario_id == data["user_pac_a"].id
        assert "exportacion" in str(log.detalle)
    finally:
        session.close()


def test_transferencia_por_paciente_distinto_del_dueno_devuelve_403(client, data):
    """Verifica que un paciente B no pueda transferir el expediente del paciente A (HTTP 403)."""
    headers_pac_b = {"Authorization": f"Bearer {data['tokens']['pac_b']}"}
    body = {"nuevo_doctor_id": str(data["doc2"].id)}

    resp = client.patch(f"/pacientes/{data['pac_a'].id}/transferir-doctor", json=body, headers=headers_pac_b)
    assert resp.status_code == 403
    assert "No autorizado" in resp.json()["detail"]


def test_flujo_transferencia_actualiza_permisos_y_auditoria(client, data):
    """Verifica que tras la transferencia, el nuevo doctor ve el historial y el anterior recibe 403."""
    headers_doc1 = {"Authorization": f"Bearer {data['tokens']['doc1']}"}
    headers_doc2 = {"Authorization": f"Bearer {data['tokens']['doc2']}"}
    headers_pac_a = {"Authorization": f"Bearer {data['tokens']['pac_a']}"}

    # 1. Antes de transferir: Doctor 1 ve al Paciente A, Doctor 2 NO lo ve (403)
    resp_doc1_pre = client.get(f"/pacientes/{data['pac_a'].id}", headers=headers_doc1)
    assert resp_doc1_pre.status_code == 200

    resp_doc2_pre = client.get(f"/pacientes/{data['pac_a'].id}", headers=headers_doc2)
    assert resp_doc2_pre.status_code == 403

    # 2. Paciente A transfiere su custodia a Doctor 2
    body = {"nuevo_doctor_id": str(data["doc2"].id)}
    resp_transfer = client.patch(f"/pacientes/{data['pac_a'].id}/transferir-doctor", json=body, headers=headers_pac_a)
    assert resp_transfer.status_code == 200
    assert resp_transfer.json()["nuevo_doctor_id"] == str(data["doc2"].id)

    # 3. Después de transferir: Doctor 2 ve al Paciente A, Doctor 1 recibe 403
    resp_doc2_post = client.get(f"/pacientes/{data['pac_a'].id}", headers=headers_doc2)
    assert resp_doc2_post.status_code == 200
    assert resp_doc2_post.json()["nombre_descifrado"] == "Paciente Titular A"

    resp_doc1_post = client.get(f"/pacientes/{data['pac_a'].id}", headers=headers_doc1)
    assert resp_doc1_post.status_code == 403

    # 4. Verificar que el Paciente A ve la transferencia reflejada en su auditoría
    resp_accesos = client.get("/pacientes/me/accesos", headers=headers_pac_a)
    assert resp_accesos.status_code == 200
    items = resp_accesos.json()["items"]
    transfer_items = [it for it in items if it["accion"] == "transferencia"]
    assert len(transfer_items) >= 1
    assert f"doctor_nuevo={data['doc2'].id}" in transfer_items[0]["detalle"]
