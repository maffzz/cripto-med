#!/usr/bin/env bash
"""": # Bash wrapper para delegar al contenedor Docker si se ejecuta en el host
if command -v docker >/dev/null 2>&1 && [ ! -f /.dockerenv ]; then
  exec docker compose run --rm backend python scripts/verificar_restauracion.py "$@"
fi
exec python3 "$0" "$@"
"""
# ==============================================================================
# CriptoMed - Verificación Forense de Restauración de Backup
# Estándares: NIST SP 800-34 (Contingency Planning), NIST SP 800-92, NIST SP 800-57
# ==============================================================================

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import DATABASE_URL
from app.crypto import decrypt
from app.audit import calcular_hash_log, format_iso_utc, GENESIS_HASH


def verificar_restauracion():
    print("=" * 65)
    print("      VERIFICACIÓN FORENSE DE INTEGRIDAD TRAS RESTAURACIÓN      ")
    print("       (NIST SP 800-34 / NIST SP 800-92 / NIST SP 800-57)       ")
    print("=" * 65)

    url_original = DATABASE_URL
    if url_original.startswith("postgresql://"):
        url_original = url_original.replace("postgresql://", "postgresql+psycopg://")

    url_restaurada = url_original.rsplit("/", 1)[0] + "/criptomed_restore_test"

    try:
        engine_orig = create_engine(url_original)
        engine_rest = create_engine(url_restaurada)
    except Exception as e:
        print(f"❌ Error al conectar a los motores de base de datos: {e}")
        return False

    fallas = 0

    # --------------------------------------------------------------------------
    # 1. Comparación de conteos de filas por tabla
    # --------------------------------------------------------------------------
    print("\n--- 1. COMPARACIÓN DE CONTEO DE FILAS ---")
    tablas = ["usuarios", "pacientes", "audit_logs", "diagnosticos_cie10"]
    print(f"{'Tabla':<25} | {'Base Original':<15} | {'Base Restaurada':<15} | {'Estado':<10}")
    print("-" * 65)

    with engine_orig.connect() as conn_orig, engine_rest.connect() as conn_rest:
        for tabla in tablas:
            try:
                cnt_orig = conn_orig.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
            except Exception:
                cnt_orig = 0
            try:
                cnt_rest = conn_rest.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
            except Exception as e:
                cnt_rest = f"Error ({e})"

            if cnt_orig == cnt_rest:
                estado = "✅ COINCIDE"
            else:
                estado = "❌ DIFERENCIA"
                fallas += 1

            print(f"{tabla:<25} | {str(cnt_orig):<15} | {str(cnt_rest):<15} | {estado}")

    # --------------------------------------------------------------------------
    # 2. Validación de la cadena criptográfica de hashes en audit_logs
    # --------------------------------------------------------------------------
    print("\n--- 2. VERIFICACIÓN DE CADENA CRIPTOGRÁFICA DE AUDITORÍA (SHA-256) ---")
    with engine_rest.connect() as conn_rest:
        logs = conn_rest.execute(text("""
            SELECT seq, id, hash_prev, hash_actual, usuario_id, accion, recurso, timestamp, ip_origen, detalle
            FROM audit_logs
            ORDER BY seq ASC
        """)).fetchall()

    if not logs:
        print("ℹ️ La tabla audit_logs restaurada está vacía. Cadena génesis intacta.")
    else:
        print(f"Verificando {len(logs)} eventos de auditoría restaurados...")
        cadena_valida = True
        ultimo_hash = GENESIS_HASH

        for row in logs:
            seq, lid, h_prev, h_actual, uid, accion, recurso, ts, ip, detalle = row
            
            # Verificar enlace con el eslabón anterior
            if h_prev != ultimo_hash:
                print(f"❌ [ESLABÓN ROTO] Fila seq={seq}: hash_prev no coincide con el anterior.")
                cadena_valida = False
                fallas += 1
                break

            ts_iso = format_iso_utc(ts)
            hash_calculado = calcular_hash_log(
                hash_prev=h_prev,
                usuario_id=uid,
                accion=str(accion),
                recurso=recurso,
                timestamp_iso=ts_iso,
                ip_origen=ip or "127.0.0.1",
                detalle=detalle or ""
            )

            if hash_calculado != h_actual:
                print(f"❌ [ALTERACIÓN DETECTADA] Fila seq={seq}: hash calculado no coincide con el guardado.")
                cadena_valida = False
                fallas += 1
                break

            ultimo_hash = h_actual

        if cadena_valida:
            print(f"✅ Cadena de auditoría 100% íntegra ({len(logs)} eventos validados criptográficamente).")

    # --------------------------------------------------------------------------
    # 3. Descifrado de muestra de 5 pacientes con llaves actuales (AES-256-GCM)
    # --------------------------------------------------------------------------
    print("\n--- 3. PRUEBA DE DESCIFRADO DE MUESTRA DE PACIENTES (AES-256-GCM + AAD) ---")
    with engine_rest.connect() as conn_rest:
        pacientes_muestra = conn_rest.execute(text("""
            SELECT id, nombre, diagnostico, medicacion
            FROM pacientes
            LIMIT 5
        """)).fetchall()

    if not pacientes_muestra:
        print("⚠️ No hay pacientes en la base de datos para probar descifrado.")
    else:
        descifrados_ok = 0
        for p in pacientes_muestra:
            pid = str(p.id)
            try:
                nom_claro = decrypt(p.nombre, aad=f"pacientes.nombre.{pid}")
                diag_claro = decrypt(p.diagnostico, aad=f"pacientes.diagnostico.{pid}")
                med_claro = decrypt(p.medicacion, aad=f"pacientes.medicacion.{pid}")
                print(f"   [OK] Paciente {pid[:8]}... -> Nombre: '{nom_claro}', Diagnóstico: '{diag_claro}'")
                descifrados_ok += 1
            except Exception as e:
                print(f"❌ [ERROR] Falló descifrado para paciente {pid}: {e}")
                fallas += 1

        print(f"✅ {descifrados_ok}/5 pacientes descifrados exitosamente con llaves y AAD actuales.")

    # --------------------------------------------------------------------------
    # Resumen Final
    # --------------------------------------------------------------------------
    print("\n" + "=" * 65)
    if fallas == 0:
        print("🎉 RESULTADO: RESTAURACIÓN Y VERIFICACIÓN FORENSE 100% EXITOSAS")
        print("   - Conteos idénticos entre producción y prueba.")
        print("   - Cadena de logs íntegra y verificada.")
        print("   - Criptografía de aplicación AES-256-GCM operativa.")
        print("=" * 65)
        return True
    else:
        print(f"❌ RESULTADO: SE ENCONTRARON {fallas} DISCREPANCIAS O FALLAS")
        print("=" * 65)
        return False


if __name__ == "__main__":
    exito = verificar_restauracion()
    sys.exit(0 if exito else 1)
