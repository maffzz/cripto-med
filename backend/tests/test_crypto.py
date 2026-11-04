"""
Pruebas unitarias para el módulo de criptografía AES-256-GCM (app/crypto.py).
Estándares verificados:
- FIPS 197 / NIST SP 800-38D (AES-GCM 256 bits).
- NIST SP 800-57 Part 1 (Gestión de llaves).
"""

import base64
import os
import secrets
import pytest
from cryptography.exceptions import InvalidTag

from app.crypto import (
    encrypt,
    decrypt,
    load_keys,
    get_current_kid,
    _b64url_encode,
    _b64url_decode,
    KEY_RING
)


@pytest.fixture(autouse=True)
def setup_crypto_keys():
    """Configura llaves v1 y v2 válidas para cada test."""
    key1_bytes = secrets.token_bytes(32)
    key2_bytes = secrets.token_bytes(32)
    k1_b64 = _b64url_encode(key1_bytes)
    k2_b64 = _b64url_encode(key2_bytes)

    enc_keys = f"v1:{k1_b64},v2:{k2_b64}"
    load_keys(enc_keys, "v2")
    yield
    # Restaurar
    load_keys(enc_keys, "v2")


def test_ida_y_vuelta_texto_vacio_tildes_emojis():
    """(a) ida y vuelta: decrypt(encrypt(x, aad), aad) == x, incluyendo texto vacío, tildes y emojis."""
    casos = [
        "",
        "Texto simple ASCII",
        "Atención médica en Perú: diagnóstico de neumonía aguda y administración de antibióticos",
        "Historial clínico con emojis: 🩺💊💉❤️🩹 Paciente estable 100% 👍",
        "Multi-línea:\nLínea 1: Síntomas\nLínea 2: Tratamiento\nLínea 3: Conclusión"
    ]
    aad = "pacientes.diagnostico.123e4567-e89b-12d3-a456-426614174000"

    for texto in casos:
        token = encrypt(texto, aad=aad)
        assert token.startswith("v2:")
        resultado = decrypt(token, aad=aad)
        assert resultado == texto

    # Prueba sin AAD
    token_sin_aad = encrypt("Dato sin aad", aad="")
    assert decrypt(token_sin_aad, aad="") == "Dato sin aad"


def test_nonce_aleatorio_salidas_distintas():
    """(b) dos cifrados del mismo texto producen salidas distintas (nonce aleatorio de 96 bits)."""
    texto = "Diagnóstico confidencial idéntico"
    aad = "pacientes.diagnostico.123e4567-e89b-12d3-a456-426614174000"

    token_1 = encrypt(texto, aad=aad)
    token_2 = encrypt(texto, aad=aad)

    # Ambos deben descifrar al mismo texto
    assert decrypt(token_1, aad=aad) == texto
    assert decrypt(token_2, aad=aad) == texto

    # Pero sus representaciones cifradas deben ser distintas por el nonce de 96 bits
    assert token_1 != token_2


def test_alterar_caracter_falla_descifrado():
    """(c) alterar un solo carácter del token provoca error al descifrar (integridad y tag)."""
    texto = "Medicamento: Amoxicilina 500mg cada 8 horas"
    aad = "pacientes.medicacion.123e4567-e89b-12d3-a456-426614174000"

    token = encrypt(texto, aad=aad)
    kid, payload = token.split(":", 1)

    # Alteramos el último carácter del payload cifrado
    caracter_original = payload[-1]
    caracter_modificado = "B" if caracter_original != "B" else "C"
    token_alterado = f"{kid}:{payload[:-1]}{caracter_modificado}"

    with pytest.raises((InvalidTag, ValueError)):
        decrypt(token_alterado, aad=aad)


def test_aad_distinto_falla_descifrado():
    """(d) usar un AAD distinto provoca error al descifrar (evita copiar tokens a otro paciente o campo)."""
    texto = "Resultado de laboratorio: Positivo para influenza"
    aad_original = "pacientes.resultado_test.paciente-uuid-001"
    aad_falso = "pacientes.resultado_test.paciente-uuid-002"
    aad_otro_campo = "pacientes.diagnostico.paciente-uuid-001"

    token = encrypt(texto, aad=aad_original)

    # Con AAD de otro paciente debe fallar
    with pytest.raises(InvalidTag):
        decrypt(token, aad=aad_falso)

    # Con AAD de otro campo debe fallar
    with pytest.raises(InvalidTag):
        decrypt(token, aad=aad_otro_campo)

    # Sin AAD debe fallar
    with pytest.raises(InvalidTag):
        decrypt(token, aad="")


def test_longitud_distinta_32_bytes_falla_arranque():
    """(e) una llave de longitud distinta de 32 bytes hace fallar el arranque con error claro."""
    # Llave de 16 bytes (128 bits) -> debe fallar porque se exige 256 bits (32 bytes)
    llave_corta = _b64url_encode(secrets.token_bytes(16))
    with pytest.raises(ValueError) as excinfo:
        load_keys(f"v1:{llave_corta}", "v1")
    assert "32 bytes" in str(excinfo.value)

    # Llave de 24 bytes (192 bits)
    llave_24 = _b64url_encode(secrets.token_bytes(24))
    with pytest.raises(ValueError) as excinfo:
        load_keys(f"v1:{llave_24}", "v1")
    assert "32 bytes" in str(excinfo.value)

    # Llave de 64 bytes (512 bits)
    llave_larga = _b64url_encode(secrets.token_bytes(64))
    with pytest.raises(ValueError) as excinfo:
        load_keys(f"v1:{llave_larga}", "v1")
    assert "32 bytes" in str(excinfo.value)


def test_token_con_kid_desconocido_falla():
    """(f) un token con kid desconocido falla con un error claro."""
    texto = "Datos de prueba con kid inexistente"
    aad = "pacientes.nombre.uuid"

    token = encrypt(texto, aad=aad)
    _, payload = token.split(":", 1)

    token_kid_falso = f"v999:{payload}"
    with pytest.raises(ValueError) as excinfo:
        decrypt(token_kid_falso, aad=aad)

    assert "v999" in str(excinfo.value)
    assert "No se encuentra en el anillo de llaves" in str(excinfo.value)
