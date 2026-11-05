#!/usr/bin/env python3
"""
Script de anonimización de datos personales después del plazo legal

Conforme a norma técnica MINSA R.M. Nº 214-2018/MINSA:
- 20 años de conservación (5 años en archivo activo + 15 años en archivo pasivo)
- Anonimización de datos personales después del plazo legal
- Conservación de datos clínicos anonimizados para investigación

Uso:
    python scripts/anonimizar_datos.py --dry-run
    python scripts/anonimizar_datos.py --execute
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid

# Configuración
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app_password@db:5432/criptomed")
PLAZO_RETENCION_YEARS = 20  # 20 años según norma técnica MINSA

def get_engine():
    """Crear engine de base de datos"""
    return create_engine(DATABASE_URL)

def get_session(engine):
    """Crear sesión de base de datos"""
    Session = sessionmaker(bind=engine)
    return Session()

def anonymize_personal_data(session, paciente_id):
    """Anonimizar datos personales de un paciente"""
    anonimizado_id = str(uuid.uuid4())[:8]

    # Campos a anonimizar (datos personales)
    paciente = session.execute(
        text("SELECT id FROM pacientes WHERE id = :id"),
        {"id": paciente_id}
    ).fetchone()

    if not paciente:
        return False

    # Anonimizar datos personales con AAD
    # NOTA: En producción, esto debería usar el sistema de cifrado existente
    # con un valor especial marcado como "ANONIMIZADO"
    try:
        session.execute(
            text("""
                UPDATE pacientes
                SET nombre = :nombre,
                    hospital = :hospital,
                    proveedor_seguro = :proveedor_seguro,
                    anonimizado = true,
                    fecha_anonimizacion = :fecha_anonimizacion
                WHERE id = :id
            """),
            {
                "nombre": f"ANONIMIZADO-{anonimizado_id}",
                "hospital": "ANONIMIZADO",
                "proveedor_seguro": "ANONIMIZADO",
                "fecha_anonimizacion": datetime.utcnow(),
                "id": paciente_id
            }
        )
        return True
    except Exception as e:
        print(f"Error anonimizando paciente {paciente_id}: {e}")
        return False

def check_retention_period(session):
    """Verificar pacientes que exceden el plazo de retención"""
    cutoff_date = datetime.utcnow() - timedelta(days=PLAZO_RETENCION_YEARS * 365)

    result = session.execute(
        text("""
            SELECT id, nombre, fecha_admision, fecha_alta, anonimizado
            FROM pacientes
            WHERE fecha_alta < :cutoff_date OR (fecha_alta IS NULL AND fecha_admision < :cutoff_date)
            ORDER BY fecha_admision
        """),
        {"cutoff_date": cutoff_date}
    ).fetchall()

    return result

def main():
    parser = argparse.ArgumentParser(description="Anonimizar datos personales después del plazo legal")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin hacer cambios")
    parser.add_argument("--execute", action="store_true", help="Ejecutar anonimización")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Error: Debes especificar --dry-run o --execute")
        sys.exit(1)

    engine = get_engine()
    session = get_session(engine)

    try:
        print(f"Verificando pacientes que exceden el plazo de retención ({PLAZO_RETENCION_YEARS} años)...")
        pacientes = check_retention_period(session)

        if not pacientes:
            print("✅ No hay pacientes que excedan el plazo de retención.")
            return

        print(f"\nEncontrados {len(pacientes)} pacientes que exceden el plazo de retención:")
        print("-" * 80)
        for p in pacientes:
            fecha_alta = p.fecha_alta if p.fecha_alta else "Activo"
            print(f"ID: {p.id}, Nombre: {p.nombre}, Admisión: {p.fecha_admision}, Alta: {fecha_alta}, Anonimizado: {p.anonimizado}")

        if args.dry_run:
            print("\n[DRY-RUN] No se realizarán cambios. Usa --execute para anonimizar.")
            return

        if args.execute:
            print("\nAnonimizando datos personales...")
            anonimizados = 0
            for p in pacientes:
                if not p.anonimizado:
                    if anonymize_personal_data(session, p.id):
                        anonimizados += 1
                        print(f"✅ Anonimizado: {p.nombre} (ID: {p.id})")

            session.commit()
            print(f"\n✅ Anonimización completada: {anonimizados} pacientes procesados.")
            print("NOTA: Datos clínicos (diagnóstico, medicación, resultado_test) se conservan anonimizados para investigación.")

    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    main()
