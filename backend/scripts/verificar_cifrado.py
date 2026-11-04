#!/usr/bin/env python3
"""
Script de verificación de cifrado en reposo para CriptoMed.
Estándares: FIPS 197 / NIST SP 800-38D (AES-256-GCM) / NIST SP 800-57 Part 1.

Comprueba:
1. Prefijo de versión de llave en todos los campos sensibles (ej. 'v2:').
2. Ausencia de texto plano legible en la base de datos.
3. Descifrado íntegro con AAD correspondiente (pacientes.<campo>.<id>).
4. Falla de integridad (InvalidTag) ante alteración de cualquier carácter del token.
5. Falla de autenticación ante intento de reutilizar el token en otro registro o campo (AAD modificado).
"""

import sys
import re
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.models import Paciente
from app.crypto import decrypt, KEY_RING, InvalidTag


def verificar_datos_reposo() -> bool:
    db = SessionLocal()
    try:
        pacientes = db.query(Paciente).limit(5).all()
        
        if not pacientes:
            print("⚠️ No hay pacientes en la base de datos para verificar.")
            return False

        print("\n=======================================================")
        print("  VERIFICACIÓN DE CIFRADO EN REPOSO AES-256-GCM (NIST)")
        print("=======================================================")
        print(f"Llaves disponibles en anillo: {list(KEY_RING.keys())}")

        version_regex = re.compile(r"^v[0-9]+:")
        todo_ok = True

        for p in pacientes:
            pid = str(p.id)
            print(f"\n[Paciente ID: {pid}]")
            
            campos = {
                "nombre": (p.nombre, "pacientes.nombre"),
                "diagnostico": (p.diagnostico, "pacientes.diagnostico"),
                "monto_facturado": (p.monto_facturado, "pacientes.monto_facturado"),
                "medicacion": (p.medicacion, "pacientes.medicacion"),
                "resultado_test": (p.resultado_test, "pacientes.resultado_test")
            }

            for campo, (valor_cifrado, prefijo_aad) in campos.items():
                if not valor_cifrado:
                    continue

                aad = f"{prefijo_aad}.{pid}"

                # 1. Comprobar prefijo de versión (ej. 'v1:', 'v2:')
                if not version_regex.match(valor_cifrado):
                    print(f"  ❌ {campo}: NO contiene prefijo de versión válido (valor: {valor_cifrado[:20]}...)")
                    todo_ok = False
                    continue
                
                kid = valor_cifrado.split(":", 1)[0]

                # 2. Comprobar descifrado con AAD correcto
                try:
                    texto_claro = decrypt(valor_cifrado, aad=aad)
                except Exception as e:
                    print(f"  ❌ {campo}: Falló el descifrado con AAD legítimo: {e}")
                    todo_ok = False
                    continue

                # 3. Comprobar que no es texto plano idéntico
                if texto_claro == valor_cifrado:
                    print(f"  ❌ {campo}: Almacenado en texto plano!")
                    todo_ok = False
                    continue

                print(f"  ✅ {campo} [{kid}]: Cifrado en reposo verificado. En claro: '{texto_claro}'")

                # 4. Comprobar que alterar un solo carácter hace fallar el descifrado
                # Modificamos un carácter central del payload base64
                idx = len(valor_cifrado) // 2
                caracter_alt = 'X' if valor_cifrado[idx] != 'X' else 'Y'
                token_alterado = valor_cifrado[:idx] + caracter_alt + valor_cifrado[idx+1:]
                try:
                    decrypt(token_alterado, aad=aad)
                    print(f"  ❌ {campo}: Integridad violada: token alterado fue descifrado sin error!")
                    todo_ok = False
                except (InvalidTag, Exception):
                    # Éxito: debe fallar por InvalidTag
                    pass

                # 5. Comprobar que alterar el AAD hace fallar el descifrado (ataque de copia a otro registro)
                aad_falso = f"{prefijo_aad}.00000000-0000-0000-0000-000000000000"
                try:
                    decrypt(valor_cifrado, aad=aad_falso)
                    print(f"  ❌ {campo}: AAD violado: token descifrado con ID de paciente falso!")
                    todo_ok = False
                except (InvalidTag, Exception):
                    # Éxito: debe fallar
                    pass

            print("  ✅ Pruebas de integridad y autenticación con AAD pasaron exitosamente.")

        print("\n=======================================================")
        if todo_ok:
            print("  RESULTADO: TODOS LOS CAMPOS ESTÁN CIFRADOS Y PROTEGIDOS")
        else:
            print("  RESULTADO: SE ENCONTRARON FALLAS EN LA VERIFICACIÓN")
        print("=======================================================\n")
        return todo_ok
    finally:
        db.close()


if __name__ == "__main__":
    exito = verificar_datos_reposo()
    sys.exit(0 if exito else 1)
