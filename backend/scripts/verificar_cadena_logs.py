#!/usr/bin/env python3
"""
Script de verificación forense de la cadena de hashes de audit_logs.
Estándares y referencias:
- NIST SP 800-92: Guide to Computer Security Log Management.
- OWASP Logging Cheat Sheet.

Recorre la tabla audit_logs por orden secuencial (seq), recalcula el hash SHA-256 de cada fila
y valida la continuidad estricta de la cadena criptográfica.
Termina con código de salida 0 si la cadena está íntegra, o 1 si se detecta cualquier alteración.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.models import AuditLog
from app.audit import calcular_hash_log, format_iso_utc, GENESIS_HASH


def verificar_cadena() -> bool:
    print("=======================================================")
    print("     VERIFICACIÓN FORENSE DE CADENA DE AUDITORÍA       ")
    print("            (NIST SP 800-92 / OWASP)                   ")
    print("=======================================================\n")

    db = SessionLocal()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.seq.asc()).all()
        total_logs = len(logs)

        if total_logs == 0:
            print("ℹ️ La tabla audit_logs está vacía. Cadena génesis intacta.")
            return True

        print(f"Total de eventos a verificar: {total_logs}\n")

        hash_prev_esperado = GENESIS_HASH

        for i, log in enumerate(logs):
            seq = log.seq
            log_id = str(log.id)

            # 1. Validar encadenamiento con el bloque anterior
            if log.hash_prev != hash_prev_esperado:
                print("❌ [FALLA DE ENCADENAMIENTO]")
                print(f"   Fila afectada : seq={seq}, id={log_id}")
                print(f"   hash_prev leído      : {log.hash_prev}")
                print(f"   hash anterior esperado: {hash_prev_esperado}")
                print("\n   => La secuencia criptográfica fue rota (posible inserción, eliminación o reordenamiento).")
                return False

            # 2. Recalcular hash_actual a partir de los datos de la fila
            ts_iso = format_iso_utc(log.timestamp)
            accion_str = log.accion.value if hasattr(log.accion, "value") else str(log.accion)

            hash_recalculado = calcular_hash_log(
                hash_prev=log.hash_prev,
                usuario_id=log.usuario_id,
                accion=accion_str,
                recurso=log.recurso,
                timestamp_iso=ts_iso,
                ip_origen=log.ip_origen,
                detalle=log.detalle
            )

            # 3. Validar integridad de los datos de la fila
            if log.hash_actual != hash_recalculado:
                print("❌ [FALLA DE INTEGRIDAD / CONTENIDO ALTERADO]")
                print(f"   Fila afectada : seq={seq}, id={log_id}")
                print(f"   Recurso       : {log.recurso}")
                print(f"   Acción        : {accion_str}")
                print(f"   Timestamp UTC : {ts_iso}")
                print(f"   Hash guardado : {log.hash_actual}")
                print(f"   Hash calculado: {hash_recalculado}")
                print("\n   => Los datos de este evento fueron modificados después de su registro original.")
                return False

            # El hash_actual de esta fila es el hash_prev esperado para la siguiente
            hash_prev_esperado = log.hash_actual

        ultimo_seq = logs[-1].seq
        ultimo_hash = logs[-1].hash_actual
        print("=======================================================")
        print(f"  ✅ CADENA ÍNTEGRA: {total_logs} eventos verificados")
        print(f"  Último Seq     : {ultimo_seq}")
        print(f"  Último Hash    : {ultimo_hash[:32]}...")
        print("=======================================================\n")
        return True

    finally:
        db.close()


def main():
    exito = verificar_cadena()
    sys.exit(0 if exito else 1)


if __name__ == "__main__":
    main()
