#!/usr/bin/env python3
"""
Smoke test end-to-end para CriptoMed
Prueba el flujo completo con cada rol contra la API local

Requisitos:
- Servicios Docker levantos (docker compose up -d)
- Datos preparados con scripts/preparar_demo.sh
- Red app_net accesible desde contenedor

Ejecutar:
docker compose run --rm --network app_net backend python tests/test_e2e_smoke.py
"""

import requests
import json
import sys
import os
from typing import Dict, Optional

# Configuración
BASE_URL = "http://backend:8000"
TIMEOUT = 10

# Credenciales desde variables de entorno (o valores por defecto para tests)
ADMIN_PASSWORD = os.getenv("DEMO_PASSWORD_ADMIN", "admin123")
DOCTOR_PASSWORD = os.getenv("DEMO_PASSWORD_DOCTOR", "admin123")
ADMINISTRATIVO_PASSWORD = os.getenv("DEMO_PASSWORD_ADMINISTRATIVO", "admin123")
AUDITOR_PASSWORD = os.getenv("DEMO_PASSWORD_AUDITOR", "admin123")
PACIENTE_PASSWORD = os.getenv("DEMO_PASSWORD_PACIENTE", "admin123")

class APIClient:
    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.email: Optional[str] = None
        self.rol: Optional[str] = None

    def login(self, email: str, password: str) -> bool:
        """Login y almacenar token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.email = email
            # Obtener info del usuario
            self._get_me()
            return True
        print(f"❌ Login falló para {email}: {response.status_code} - {response.text}")
        return False

    def _get_me(self):
        """Obtener información del usuario actual"""
        if not self.token:
            return None
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            self.user_id = data["id"]
            self.rol = data["rol"]
            return data
        return None

    def get_pacientes(self) -> Dict:
        """Obtener lista de pacientes"""
        response = requests.get(
            f"{BASE_URL}/api/pacientes",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=TIMEOUT
        )
        return response.json() if response.status_code == 200 else None

    def get_audit_logs(self) -> Dict:
        """Obtener logs de auditoría"""
        response = requests.get(
            f"{BASE_URL}/api/audit-logs",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=TIMEOUT
        )
        return response.json() if response.status_code == 200 else None

    def verify_cadena_logs(self) -> bool:
        """Verificar cadena de logs"""
        response = requests.get(
            f"{BASE_URL}/api/audit-logs/verificar-cadena",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("valida", False)
        return False

    def transferir_doctor(self, paciente_id: str, nuevo_doctor_id: str) -> bool:
        """Transferir paciente a otro doctor"""
        response = requests.patch(
            f"{BASE_URL}/api/pacientes/{paciente_id}/transferir-doctor",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"nuevo_doctor_id": nuevo_doctor_id},
            timeout=TIMEOUT
        )
        return response.status_code == 200

    def get_paciente_me(self) -> Dict:
        """Obtener propio historial (paciente)"""
        response = requests.get(
            f"{BASE_URL}/api/pacientes/me",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=TIMEOUT
        )
        return response.json() if response.status_code == 200 else None

def test_1_login_doctor_a():
    """Test 1: Login como Doctor A (Dra. Ana Torres)"""
    print("\n[Test 1] Login como Doctor A (Dra. Ana Torres)")
    client = APIClient()
    if client.login("ana.torres@criptomed.local", DOCTOR_PASSWORD):
        print(f"✅ Login exitoso - Rol: {client.rol}")
        assert client.rol == "doctor", f"Rol incorrecto: {client.rol}"
        return client
    return None

def test_2_lista_pacientes_doctor_a(client: APIClient):
    """Test 2: Doctor A ve sus pacientes (incluyendo Paciente Demo)"""
    print("\n[Test 2] Doctor A ve sus pacientes")
    pacientes = client.get_pacientes()
    if pacientes and "items" in pacientes:
        print(f"✅ Doctor A ve {len(pacientes['items'])} pacientes")
        # Verificar que Paciente Demo esté en la lista
        paciente_demo = next((p for p in pacientes["items"] if "Paciente Demo" in p.get("nombre_descifrado", "")), None)
        if paciente_demo:
            print(f"✅ Paciente Demo está en la lista de Doctor A")
            return paciente_demo["id"]
        else:
            print("❌ Paciente Demo NO está en la lista de Doctor A")
            return None
    else:
        print("❌ Error obteniendo pacientes")
        return None

def test_3_login_doctor_b():
    """Test 3: Login como Doctor B (Dr. Luis Ramírez)"""
    print("\n[Test 3] Login como Doctor B (Dr. Luis Ramírez)")
    client = APIClient()
    if client.login("luis.ramirez@criptomed.local", DOCTOR_PASSWORD):
        print(f"✅ Login exitoso - Rol: {client.rol}")
        assert client.rol == "doctor", f"Rol incorrecto: {client.rol}"
        return client
    return None

def test_4_doctor_b_no_ve_paciente_demo(client: APIClient):
    """Test 4: Doctor B NO ve al paciente demo"""
    print("\n[Test 4] Doctor B NO ve al paciente demo")
    pacientes = client.get_pacientes()
    if pacientes and "items" in pacientes:
        paciente_demo = next((p for p in pacientes["items"] if "Paciente Demo" in p.get("nombre_descifrado", "")), None)
        if paciente_demo:
            print("❌ Doctor B VE al paciente demo (ERROR: no debería verlo)")
            return False
        else:
            print("✅ Doctor B NO ve al paciente demo (correcto)")
            return True
    else:
        print("❌ Error obteniendo pacientes")
        return False

def test_5_login_administrativo():
    """Test 5: Login como administrativo"""
    print("\n[Test 5] Login como administrativo")
    client = APIClient()
    if client.login("admin1@criptomed.local", ADMINISTRATIVO_PASSWORD):
        print(f"✅ Login exitoso - Rol: {client.rol}")
        assert client.rol == "administrativo", f"Rol incorrecto: {client.rol}"
        return client
    return None

def test_6_administrativo_sin_campos_clinicos(client: APIClient):
    """Test 6: Administrativo NO ve campos clínicos (diagnóstico, medicación, resultado_test)"""
    print("\n[Test 6] Administrativo NO ve campos clínicos")
    pacientes = client.get_pacientes()
    if pacientes and "items" in pacientes:
        # Verificar que ningún paciente tenga campos clínicos
        for p in pacientes["items"]:
            if p.get("diagnostico_descifrado") or p.get("medicacion_descifrado") or p.get("resultado_test_descifrado"):
                print(f"❌ Administrativo VE campos clínicos en paciente {p.get('nombre_descifrado')}")
                return False
        print("✅ Administrativo NO ve campos clínicos (correcto)")
        return True
    else:
        print("❌ Error obteniendo pacientes")
        return False

def test_7_login_paciente():
    """Test 7: Login como paciente"""
    print("\n[Test 7] Login como paciente (Paciente Demo)")
    client = APIClient()
    if client.login("paciente1@criptomed.local", PACIENTE_PASSWORD):
        print(f"✅ Login exitoso - Rol: {client.rol}")
        assert client.rol == "paciente", f"Rol incorrecto: {client.rol}"
        return client
    return None

def test_8_paciente_transfiere_a_doctor_b(client: APIClient, doctor_b_id: str):
    """Test 8: Paciente transfiere a Doctor B"""
    print("\n[Test 8] Paciente transfiere a Doctor B")
    # Primero obtener el paciente_id del paciente
    paciente_info = client.get_paciente_me()
    if not paciente_info:
        print("❌ Error obteniendo propio historial")
        return False, None
    
    paciente_id = paciente_info["id"]
    
    # Obtener lista de doctores
    response = requests.get(
        f"{BASE_URL}/api/pacientes/doctores",
        headers={"Authorization": f"Bearer {client.token}"},
        timeout=TIMEOUT
    )
    if response.status_code != 200:
        print("❌ Error obteniendo lista de doctores")
        return False, None
    
    doctores = response.json()
    doctor_b = next((d for d in doctores if "Luis Ramírez" in d.get("nombre", "")), None)
    if not doctor_b:
        print("❌ Doctor B no encontrado en lista")
        return False, None
    
    if client.transferir_doctor(paciente_id, doctor_b["id"]):
        print(f"✅ Transferencia exitosa a Dr. Luis Ramírez")
        return True, doctor_b["id"]
    else:
        print("❌ Transferencia falló")
        return False, None

def test_9_doctor_b_ahora_ve_paciente():
    """Test 9: Doctor B ahora ve al paciente"""
    print("\n[Test 9] Doctor B ahora ve al paciente")
    client = APIClient()
    if client.login("luis.ramirez@criptomed.local", DOCTOR_PASSWORD):
        pacientes = client.get_pacientes()
        if pacientes and "items" in pacientes:
            paciente_demo = next((p for p in pacientes["items"] if "Paciente Demo" in p.get("nombre_descifrado", "")), None)
            if paciente_demo:
                print("✅ Doctor B AHORA ve al paciente demo (correcto)")
                return True
            else:
                print("❌ Doctor B NO ve al paciente demo (error)")
                return False
    return False

def test_10_doctor_a_ya_no_ve_paciente():
    """Test 10: Doctor A ya no ve al paciente"""
    print("\n[Test 10] Doctor A ya no ve al paciente")
    client = APIClient()
    if client.login("ana.torres@criptomed.local", DOCTOR_PASSWORD):
        pacientes = client.get_pacientes()
        if pacientes and "items" in pacientes:
            paciente_demo = next((p for p in pacientes["items"] if "Paciente Demo" in p.get("nombre_descifrado", "")), None)
            if paciente_demo:
                print("❌ Doctor A AÚN ve al paciente demo (error)")
                return False
            else:
                print("✅ Doctor A YA NO ve al paciente demo (correcto)")
                return True
    return False

def test_11_login_auditor():
    """Test 11: Login como auditor"""
    print("\n[Test 11] Login como auditor")
    client = APIClient()
    if client.login("auditor1@criptomed.local", AUDITOR_PASSWORD):
        print(f"✅ Login exitoso - Rol: {client.rol}")
        assert client.rol == "auditor", f"Rol incorrecto: {client.rol}"
        return client
    return None

def test_12_auditor_ve_evento_transferencia(client: APIClient):
    """Test 12: Auditor ve evento de transferencia"""
    print("\n[Test 12] Auditor ve evento de transferencia")
    logs = client.get_audit_logs()
    if logs and "items" in logs:
        # Buscar evento de transferencia
        transferencia = next((l for l in logs["items"] if l["accion"] == "transferencia"), None)
        if transferencia:
            print(f"✅ Auditor ve evento de transferencia (seq: {transferencia['seq']})")
            return True
        else:
            print("❌ Auditor NO ve evento de transferencia")
            return False
    else:
        print("❌ Error obteniendo logs")
        return False

def test_13_cadena_logs_valida(client: APIClient):
    """Test 13: Cadena de logs es válida"""
    print("\n[Test 13] Verificar cadena de logs")
    if client.verify_cadena_logs():
        print("✅ Cadena de logs válida")
        return True
    else:
        print("❌ Cadena de logs inválida")
        return False

def test_14_token_revocado():
    """Test 14: Token revocado deja de funcionar"""
    print("\n[Test 14] Token revocado deja de funcionar")
    # Login, luego revocar usuario, luego intentar usar token
    client = APIClient()
    if client.login("ana.torres@criptomed.local", DOCTOR_PASSWORD):
        # Revocar usuario
        response = requests.patch(
            f"{BASE_URL}/api/usuarios/{client.user_id}/revocar",
            headers={"Authorization": f"Bearer {client.token}"},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            # Intentar usar token revocado
            pacientes = client.get_pacientes()
            if pacientes is None or "detail" in pacientes:
                print("✅ Token revocado deja de funcionar (correcto)")
                return True
            else:
                print("❌ Token revocado aún funciona (error)")
                return False
        else:
            print("❌ Error revocando usuario")
            return False
    return False

def main():
    print("=" * 60)
    print("Smoke Test End-to-End - CriptoMed")
    print("=" * 60)
    
    results = []
    
    # Test 1-2: Doctor A
    doctor_a = test_1_login_doctor_a()
    if doctor_a:
        paciente_id = test_2_lista_pacientes_doctor_a(doctor_a)
        results.append(("Doctor A login", True))
        results.append(("Doctor A ve Paciente Demo", paciente_id is not None))
    else:
        results.append(("Doctor A login", False))
        results.append(("Doctor A ve Paciente Demo", False))
    
    # Test 3-4: Doctor B
    doctor_b = test_3_login_doctor_b()
    if doctor_b:
        test_4_result = test_4_doctor_b_no_ve_paciente_demo(doctor_b)
        results.append(("Doctor B login", True))
        results.append(("Doctor B NO ve Paciente Demo", test_4_result))
    else:
        results.append(("Doctor B login", False))
        results.append(("Doctor B NO ve Paciente Demo", False))
    
    # Test 5-6: Administrativo
    administrativo = test_5_login_administrativo()
    if administrativo:
        test_6_result = test_6_administrativo_sin_campos_clinicos(administrativo)
        results.append(("Administrativo login", True))
        results.append(("Administrativo sin campos clínicos", test_6_result))
    else:
        results.append(("Administrativo login", False))
        results.append(("Administrativo sin campos clínicos", False))
    
    # Test 7-8: Paciente
    paciente = test_7_login_paciente()
    if paciente:
        # Necesitamos doctor_b_id para transferencia
        # Primero obtener IDs de doctores
        client_temp = APIClient()
        client_temp.login("luis.ramirez@criptomed.local", DOCTOR_PASSWORD)
        user_info = client_temp._get_me()
        doctor_b_id = user_info["id"] if user_info else None
        
        if doctor_b_id:
            test_8_result, _ = test_8_paciente_transfiere_a_doctor_b(paciente, doctor_b_id)
            results.append(("Paciente login", True))
            results.append(("Paciente transfiere a Doctor B", test_8_result))
        else:
            results.append(("Paciente login", True))
            results.append(("Paciente transfiere a Doctor B", False))
    else:
        results.append(("Paciente login", False))
        results.append(("Paciente transfiere a Doctor B", False))
    
    # Test 9-10: Verificación de transferencia
    test_9_result = test_9_doctor_b_ahora_ve_paciente()
    test_10_result = test_10_doctor_a_ya_no_ve_paciente()
    results.append(("Doctor B ahora ve Paciente Demo", test_9_result))
    results.append(("Doctor A ya no ve Paciente Demo", test_10_result))
    
    # Test 11-13: Auditor
    auditor = test_11_login_auditor()
    if auditor:
        test_12_result = test_12_auditor_ve_evento_transferencia(auditor)
        test_13_result = test_13_cadena_logs_valida(auditor)
        results.append(("Auditor login", True))
        results.append(("Auditor ve transferencia", test_12_result))
        results.append(("Cadena de logs válida", test_13_result))
    else:
        results.append(("Auditor login", False))
        results.append(("Auditor ve transferencia", False))
        results.append(("Cadena de logs válida", False))
    
    # Test 14: Token revocado
    test_14_result = test_14_token_revocado()
    results.append(("Token revocado deja de funcionar", test_14_result))
    
    # Resumen
    print("\n" + "=" * 60)
    print("Resumen de resultados")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\n🎉 Todos los tests pasaron")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} tests fallaron")
        sys.exit(1)

if __name__ == "__main__":
    main()
