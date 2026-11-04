#!/usr/bin/env python3
"""
Script de rotación de llaves criptográficas para CriptoMed.
Estándares y referencias:
- NIST SP 800-57 Part 1: Recommendation for Key Management (Cryptoperiod & Key Rotation).
- NIST SP 800-38D: Galois/Counter Mode (GCM).

Re-cifra campos sensibles en la tabla pacientes hacia la versión activa (ENC_KEY_CURRENT).
Soporta:
- Procesamiento en lotes (batch) con commit independiente por lote.
- Opción --dry-run para simulación sin escrituras.
- Idempotencia total: ejecutarlo múltiples veces no corrompe ni re-cifra datos ya actualizados.
- Aborto seguro por lote ante fallo de autenticación de cualquier registro.
"""

import sys
import os
import argparse
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.models import Paciente
from app.crypto import encrypt, decrypt, get_current_kid, KEY_RING, InvalidTag

CAMPOS_SENSIBLES = [
    ("nombre", "pacientes.nombre"),
    ("diagnostico", "pacientes.diagnostico"),
    ("monto_facturado", "pacientes.monto_facturado"),
    ("medicacion", "pacientes.medicacion"),
    ("resultado_test", "pacientes.resultado_test")
]


def rotar_llaves(batch_size: int = 500, dry_run: bool = False) -> dict:
    current_kid = get_current_kid()
    prefijo_actual = f"{current_kid}:"

    print("=======================================================")
    print("      ROTACIÓN DE LLAVES EN REPOSO (NIST SP 800-57)    ")
    print("=======================================================")
    print(f"Llave activa destino (ENC_KEY_CURRENT): '{current_kid}'")
    print(f"Llaves disponibles en anillo          : {list(KEY_RING.keys())}")
    print(f"Tamaño de lote (batch size)           : {batch_size}")
    print(f"Modo de ejecución                     : {'DRY-RUN (Simulación sin escritura)' if dry_run else 'EN VIVO (Escritura en BD)'}")
    print("=======================================================\n")

    db = SessionLocal()
    estadisticas = {
        "registros_revisados": 0,
        "campos_migrados": 0,
        "campos_ya_actualizados": 0,
        "errores": 0,
        "lotes_procesados": 0
    }

    try:
        total_pacientes = db.query(Paciente).count()
        print(f"Total de registros a evaluar: {total_pacientes}\n")

        offset = 0
        while offset < total_pacientes:
            lote = db.query(Paciente).order_by(Paciente.id).offset(offset).limit(batch_size).all()
            if not lote:
                break

            estadisticas["lotes_procesados"] += 1
            print(f"--- Procesando Lote {estadisticas['lotes_procesados']} (offset {offset} a {offset + len(lote)}) ---")

            try:
                for paciente in lote:
                    estadisticas["registros_revisados"] += 1
                    pid = str(paciente.id)

                    for nombre_campo, prefijo_aad in CAMPOS_SENSIBLES:
                        valor_actual = getattr(paciente, nombre_campo)
                        if not valor_actual:
                            continue

                        # Si ya tiene el prefijo de la llave actual, no requiere re-cifrado
                        if valor_actual.startswith(prefijo_actual):
                            estadisticas["campos_ya_actualizados"] += 1
                            continue

                        aad = f"{prefijo_aad}.{pid}"

                        # Descifrar con la llave histórica y su AAD
                        try:
                            texto_claro = decrypt(valor_actual, aad=aad)
                        except Exception as e:
                            print(f"  ❌ ERROR crítico de descifrado en Paciente {pid}, campo '{nombre_campo}': {e}")
                            print(f"     Se aborta el lote {estadisticas['lotes_procesados']} para preservar integridad.")
                            raise

                        # Re-cifrar con la nueva llave activa y el mismo AAD
                        nuevo_cifrado = encrypt(texto_claro, aad=aad)

                        if not dry_run:
                            setattr(paciente, nombre_campo, nuevo_cifrado)

                        estadisticas["campos_migrados"] += 1

                if not dry_run:
                    db.commit()
                    print(f"  ✅ Lote {estadisticas['lotes_procesados']} persistido exitosamente (commit).")
                else:
                    db.rollback()
                    print(f"  [DRY-RUN] Lote {estadisticas['lotes_procesados']} simulado exitosamente (rollback).")

            except Exception:
                db.rollback()
                estadisticas["errores"] += 1
                print(f"  ❌ Lote {estadisticas['lotes_procesados']} revertido (rollback). No se modificaron datos.")
                break

            offset += batch_size

    finally:
        db.close()

    print("\n=======================================================")
    print("               RESUMEN DE ROTACIÓN                     ")
    print("=======================================================")
    print(f"Registros revisados            : {estadisticas['registros_revisados']}")
    print(f"Campos migrados a '{current_kid}'        : {estadisticas['campos_migrados']}")
    print(f"Campos ya en versión actual    : {estadisticas['campos_ya_actualizados']}")
    print(f"Lotes procesados exitosamente  : {estadisticas['lotes_procesados'] - estadisticas['errores']}")
    print(f"Errores encontrados            : {estadisticas['errores']}")
    print("=======================================================\n")

    return estadisticas


def main():
    parser = argparse.ArgumentParser(description="Rotación de llaves de cifrado en reposo para CriptoMed.")
    parser.add_argument("--batch-size", type=int, default=500, help="Cantidad de pacientes por lote (default: 500)")
    parser.add_argument("--dry-run", action="store_true", help="Simula la rotación sin escribir cambios en la BD")
    args = parser.parse_args()

    stats = rotar_llaves(batch_size=args.batch_size, dry_run=args.dry_run)
    sys.exit(0 if stats["errores"] == 0 else 1)


if __name__ == "__main__":
    main()
