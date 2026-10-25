"""
Pruebas parametrizadas por rol para el endpoint de pacientes.
Verifica que cada rol vea los campos correctos y reciba los códigos HTTP adecuados.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.main import app
from app.database import SessionLocal, engine, Base
from app.models import Usuario, Paciente, RolEnum
from app.auth import get_password_hash


@pytest.fixture(scope="function")
def db():
    """Fixture para crear una sesión de base de datos."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Fixture para crear un cliente de prueba."""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_users(db):
    """Fixture para crear usuarios de prueba por rol."""
    users = {}
    
    # Admin
    admin = Usuario(
        email="admin@test.com",
        nombre="Admin Test",
        password_hash=get_password_hash("admin123"),
        rol=RolEnum.admin,
        activo=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    users["admin"] = admin
    
    # Doctor
    doctor = Usuario(
        email="doctor@test.com",
        nombre="Doctor Test",
        password_hash=get_password_hash("doctor123"),
        rol=RolEnum.doctor,
        activo=True
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    users["doctor"] = doctor
    
    # Administrativo
    administrativo = Usuario(
        email="admini@test.com",
        nombre="Administrativo Test",
        password_hash=get_password_hash("admini123"),
        rol=RolEnum.administrativo,
        activo=True
    )
    db.add(administrativo)
    db.commit()
    db.refresh(administrativo)
    users["administrativo"] = administrativo
    
    # Auditor
    auditor = Usuario(
        email="auditor@test.com",
        nombre="Auditor Test",
        password_hash=get_password_hash("auditor123"),
        rol=RolEnum.auditor,
        activo=True
    )
    db.add(auditor)
    db.commit()
    db.refresh(auditor)
    users["auditor"] = auditor
    
    # Paciente
    paciente_usuario = Usuario(
        email="paciente@test.com",
        nombre="Paciente Test",
        password_hash=get_password_hash("paciente123"),
        rol=RolEnum.paciente,
        activo=True
    )
    db.add(paciente_usuario)
    db.commit()
    db.refresh(paciente_usuario)
    users["paciente"] = paciente_usuario
    
    return users


@pytest.fixture(scope="function")
def test_pacientes(db, test_users):
    """Fixture para crear pacientes de prueba."""
    from app.crypto import encrypt
    
    # Paciente asignado al doctor (sin código_cie10 para evitar foreign key constraint)
    paciente_asignado = Paciente(
        edad=30,
        genero="F",
        tipo_sangre="O+",
        codigo_cie10=None,  # None para evitar foreign key constraint
        fecha_admision="2024-01-01",
        hospital="Hospital Test",
        proveedor_seguro="Seguro Test",
        numero_habitacion="101",
        tipo_admision="Urgencia",
        fecha_alta=None,
        doctor_id=test_users["doctor"].id,
        nombre=encrypt("Maria Test"),
        diagnostico=encrypt("Gripe estomacal"),
        monto_facturado=encrypt("1500.00"),
        medicacion=encrypt("Paracetamol 500mg"),
        resultado_test=encrypt("Negativo")
    )
    db.add(paciente_asignado)
    db.commit()
    db.refresh(paciente_asignado)
    
    # Paciente asignado a otro doctor
    otro_doctor = Usuario(
        email="otro_doctor@test.com",
        nombre="Otro Doctor",
        password_hash=get_password_hash("doctor123"),
        rol=RolEnum.doctor,
        activo=True
    )
    db.add(otro_doctor)
    db.commit()
    db.refresh(otro_doctor)
    
    paciente_no_asignado = Paciente(
        edad=40,
        genero="M",
        tipo_sangre="A+",
        codigo_cie10=None,  # None para evitar foreign key constraint
        fecha_admision="2024-01-02",
        hospital="Hospital Test",
        proveedor_seguro="Seguro Test",
        numero_habitacion="102",
        tipo_admision="Programado",
        fecha_alta=None,
        doctor_id=otro_doctor.id,
        nombre=encrypt("Juan Test"),
        diagnostico=encrypt("Neumonia"),
        monto_facturado=encrypt("2000.00"),
        medicacion=encrypt("Antibiotico"),
        resultado_test=encrypt("Positivo")
    )
    db.add(paciente_no_asignado)
    db.commit()
    db.refresh(paciente_no_asignado)
    
    return {
        "asignado": paciente_asignado,
        "no_asignado": paciente_no_asignado
    }


def get_auth_token(client, email, password):
    """Helper para obtener token de autenticación."""
    response = client.post("/auth/login", data={
        "username": email,
        "password": password
    })
    return response.json()["access_token"]


class TestPacientesPorRol:
    """Pruebas parametrizadas por rol para endpoints de pacientes."""
    
    @pytest.mark.parametrize("rol,email,password,esperado_campos_sensibles", [
        (RolEnum.admin, "admin@test.com", "admin123", True),
        (RolEnum.doctor, "doctor@test.com", "doctor123", True),
        (RolEnum.administrativo, "admini@test.com", "admini123", False),
    ])
    def test_listar_pacientes_campos_rol(
        self, client, test_users, test_pacientes, rol, email, password, esperado_campos_sensibles
    ):
        """Test que verifica que cada rol vea los campos correctos en GET /pacientes."""
        token = get_auth_token(client, email, password)
        
        response = client.get("/pacientes", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        pacientes = response.json()
        assert len(pacientes) > 0
        
        paciente = pacientes[0]
        
        # Campos básicos deben estar presentes para todos
        assert "id" in paciente
        assert "edad" in paciente
        assert "genero" in paciente
        assert "nombre_descifrado" in paciente
        assert "monto_facturado_descifrado" in paciente
        
        # Campos sensibles según rol
        if esperado_campos_sensibles:
            assert "diagnostico_descifrado" in paciente
            assert "medicacion_descifrado" in paciente
            assert "resultado_test_descifrado" in paciente
        else:
            # Administrativo NO debe ver campos sensibles
            assert "diagnostico_descifrado" not in paciente
            assert "medicacion_descifrado" not in paciente
            assert "resultado_test_descifrado" not in paciente
    
    @pytest.mark.parametrize("rol,email,password,http_code", [
        (RolEnum.admin, "admin@test.com", "admin123", 200),
        (RolEnum.doctor, "doctor@test.com", "doctor123", 200),
        (RolEnum.administrativo, "admini@test.com", "admini123", 200),
        (RolEnum.auditor, "auditor@test.com", "auditor123", 403),
    ])
    def test_listar_pacientes_http_code(
        self, client, test_users, test_pacientes, rol, email, password, http_code
    ):
        """Test que verifica que cada rol reciba el código HTTP correcto en GET /pacientes."""
        token = get_auth_token(client, email, password)
        
        response = client.get("/pacientes", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == http_code
    
    @pytest.mark.parametrize("rol,email,password,http_code,esperado_campos_sensibles", [
        (RolEnum.admin, "admin@test.com", "admin123", 200, True),
        (RolEnum.doctor, "doctor@test.com", "doctor123", 200, True),
        (RolEnum.administrativo, "admini@test.com", "admini123", 200, False),
        (RolEnum.auditor, "auditor@test.com", "auditor123", 403, False),
    ])
    def test_obtener_paciente_campos_rol(
        self, client, test_users, test_pacientes, rol, email, password, http_code, esperado_campos_sensibles
    ):
        """Test que verifica que cada rol vea los campos correctos en GET /pacientes/{id}."""
        token = get_auth_token(client, email, password)
        
        paciente_id = test_pacientes["asignado"].id
        response = client.get(f"/pacientes/{paciente_id}", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == http_code
        
        if http_code == 200:
            paciente = response.json()
            
            # Campos básicos deben estar presentes
            assert "id" in paciente
            assert "edad" in paciente
            assert "genero" in paciente
            assert "nombre_descifrado" in paciente
            assert "monto_facturado_descifrado" in paciente
            
            # Campos sensibles según rol
            if esperado_campos_sensibles:
                assert "diagnostico_descifrado" in paciente
                assert "medicacion_descifrado" in paciente
                assert "resultado_test_descifrado" in paciente
            else:
                # Administrativo NO debe ver campos sensibles
                assert "diagnostico_descifrado" not in paciente
                assert "medicacion_descifrado" not in paciente
                assert "resultado_test_descifrado" not in paciente
    
    def test_doctor_solo_ve_pacientes_asignados(self, client, test_users, test_pacientes):
        """Test que verifica que el doctor solo ve sus pacientes asignados."""
        token = get_auth_token(client, "doctor@test.com", "doctor123")
        
        response = client.get("/pacientes", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        pacientes = response.json()
        
        # Solo debe ver el paciente asignado a él
        assert len(pacientes) == 1
        assert str(pacientes[0]["id"]) == str(test_pacientes["asignado"].id)
        assert pacientes[0]["doctor_id"] == str(test_users["doctor"].id)
    
    def test_doctor_no_puede_ver_paciente_no_asignado(self, client, test_users, test_pacientes):
        """Test que verifica que el doctor no puede ver pacientes no asignados."""
        token = get_auth_token(client, "doctor@test.com", "doctor123")
        
        paciente_no_asignado_id = test_pacientes["no_asignado"].id
        response = client.get(f"/pacientes/{paciente_no_asignado_id}", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 403
