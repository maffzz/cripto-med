"""
Módulo de Criptografía de CriptoMed.
Implementa cifrado autenticado en reposo con AES-256-GCM y llaves versionadas.
Estándares y referencias:
- FIPS 197: Advanced Encryption Standard (AES) con llave de 256 bits.
- NIST SP 800-38D: Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM).
- NIST SP 800-57 Part 1: Recommendation for Key Management (ciclo de vida y rotación de llaves).
"""

import base64
import os
from typing import Dict, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# Diccionario global para el anillo de llaves y llave actual
KEY_RING: Dict[str, AESGCM] = {}
CURRENT_KID: str = ""


def _b64url_decode(s: str) -> bytes:
    """Decodifica una cadena base64url con o sin padding."""
    rem = len(s) % 4
    if rem > 0:
        s += "=" * (4 - rem)
    return base64.urlsafe_b64decode(s)


def _b64url_encode(data: bytes) -> str:
    """Codifica bytes en base64url sin padding."""
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def load_keys(enc_keys_raw: Optional[str] = None, current_kid_raw: Optional[str] = None) -> None:
    """
    Carga y valida el anillo de llaves desde variables o parámetros.
    Formato esperado de enc_keys_raw: "v1:<b64url_32bytes>,v2:<b64url_32bytes>"
    Valida que cada llave decodifique a EXACTAMENTE 32 bytes (256 bits).
    """
    global KEY_RING, CURRENT_KID

    if enc_keys_raw is None:
        enc_keys_raw = os.getenv("ENC_KEYS", "")
    if current_kid_raw is None:
        current_kid_raw = os.getenv("ENC_KEY_CURRENT", "")

    enc_keys_raw = enc_keys_raw.strip()
    current_kid_raw = current_kid_raw.strip()

    if not enc_keys_raw:
        # Si no hay llaves configuradas, inicializar con una de respaldo para testing/desarrollo
        # pero permitiendo reconfiguración
        KEY_RING = {}
        CURRENT_KID = ""
        return

    new_ring: Dict[str, AESGCM] = {}
    key_entries = [entry.strip() for entry in enc_keys_raw.split(",") if entry.strip()]

    for entry in key_entries:
        if ":" not in entry:
            raise ValueError(f"Formato de entrada de llave inválido en ENC_KEYS: '{entry}'. Se espera 'kid:base64url'")
        kid, b64_key = entry.split(":", 1)
        kid = kid.strip()
        b64_key = b64_key.strip()
        
        try:
            key_bytes = _b64url_decode(b64_key)
        except Exception as e:
            raise ValueError(f"Error al decodificar la llave '{kid}' en base64url: {e}")

        if len(key_bytes) != 32:
            raise ValueError(
                f"La llave '{kid}' decodifica a {len(key_bytes)} bytes. "
                f"AES-256 requiere exactamente 32 bytes (256 bits)."
            )

        new_ring[kid] = AESGCM(key_bytes)

    if not new_ring:
        raise ValueError("No se pudo cargar ninguna llave válida desde ENC_KEYS.")

    if not current_kid_raw:
        # Si no se especificó llave actual, tomar la última del anillo
        current_kid_raw = list(new_ring.keys())[-1]
    elif current_kid_raw not in new_ring:
        raise ValueError(
            f"ENC_KEY_CURRENT='{current_kid_raw}' no coincide con ninguna llave disponible en ENC_KEYS: {list(new_ring.keys())}"
        )

    KEY_RING = new_ring
    CURRENT_KID = current_kid_raw


def get_current_kid() -> str:
    """Retorna el identificador de la llave activa actual."""
    return CURRENT_KID


def encrypt(plaintext: Optional[str], aad: str = "") -> str:
    """
    Cifra texto usando AES-256-GCM con la llave actual del anillo.
    
    Args:
        plaintext: Texto a cifrar (puede ser texto vacío). Si es None, retorna "".
        aad: Datos Asociados Autenticados (ej. 'pacientes.<campo>.<id_paciente>').
             Evita copiar el valor cifrado a otro registro o columna.
             
    Returns:
        Cadena en formato '<kid>:<base64url(nonce + ciphertext_con_tag)>'.
    """
    if plaintext is None:
        return ""

    if not KEY_RING or not CURRENT_KID:
        load_keys()

    if not KEY_RING or not CURRENT_KID:
        raise RuntimeError("El anillo de llaves no está inicializado. Configure ENC_KEYS y ENC_KEY_CURRENT.")

    # Nonce aleatorio de 96 bits (12 bytes) según recomendación NIST SP 800-38D
    nonce = os.urandom(12)
    aesgcm = KEY_RING[CURRENT_KID]
    aad_bytes = aad.encode("utf-8") if aad else None

    # AESGCM.encrypt genera el ciphertext concatenado con el tag de autenticación (16 bytes)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), aad_bytes)
    
    payload = _b64url_encode(nonce + ciphertext_with_tag)
    return f"{CURRENT_KID}:{payload}"


def decrypt(token: Optional[str], aad: str = "") -> str:
    """
    Descifra un token cifrado con AES-256-GCM verificando su autenticidad e integridad.
    
    Args:
        token: Cadena '<kid>:<base64url(nonce + ciphertext_con_tag)>'.
        aad: Mismo AAD usado al momento del cifrado.
        
    Returns:
        Texto descifrado en claro.
        
    Raises:
        InvalidTag: Si el texto cifrado o el AAD han sido alterados (integridad violada).
        ValueError: Si el token está malformado, truncado o el kid es desconocido.
    """
    if not token:
        return ""

    if not KEY_RING:
        load_keys()

    if ":" not in token:
        raise ValueError("Formato de token inválido: falta separador 'kid:payload'.")

    kid, payload_b64 = token.split(":", 1)
    if kid not in KEY_RING:
        raise ValueError(f"Llave desconocida con kid='{kid}'. No se encuentra en el anillo de llaves.")

    payload = _b64url_decode(payload_b64)
    if len(payload) < 28:
        # 12 bytes de nonce + 16 bytes de tag de autenticación mínimo
        raise ValueError("Token inválido o truncado: longitud insuficiente para nonce y tag de autenticación.")

    nonce = payload[:12]
    ciphertext_with_tag = payload[12:]
    aesgcm = KEY_RING[kid]
    aad_bytes = aad.encode("utf-8") if aad else None

    # Si la verificación de integridad falla, AESGCM lanza InvalidTag y no devuelve datos parciales
    plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, aad_bytes)
    return plaintext_bytes.decode("utf-8")


# Inicialización al importar el módulo
try:
    load_keys()
except Exception:
    # Si las variables aún no están en el entorno durante ciertas importaciones,
    # load_keys se invocará bajo demanda al momento de cifrar/descifrar.
    pass
