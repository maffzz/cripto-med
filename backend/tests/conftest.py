"""
Configuración de pytest para el proyecto CriptoMed.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio padre al path para poder importar app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.limiter import limiter
# Desactivar rate limiting por defecto para suites masivas de tests
limiter.enabled = False

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def get_owner_engine():
    """
    Crea un engine con OWNER_DATABASE_URL para operaciones privilegiadas en tests
    (DISABLE/ENABLE TRIGGER, DELETE en tablas protegidas).
    Cae en DATABASE_URL si la variable de entorno no está definida.
    """
    url = os.getenv("OWNER_DATABASE_URL") or os.getenv("DATABASE_URL", "")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://")
    return create_engine(url, pool_pre_ping=True)


@pytest.fixture(scope="session")
def owner_engine():
    """Engine con privilegios de owner, reutilizado en toda la sesión de tests."""
    return get_owner_engine()


@pytest.fixture
def clean_audit_logs(owner_engine):
    """
    Fixture reutilizable: desactiva el trigger de audit_logs, borra todos los
    registros y lo reactiva — usando el rol dueño (OWNER_DATABASE_URL).
    Ideal para tests que necesitan la tabla vacía.
    """
    OSession = sessionmaker(bind=owner_engine)
    s = OSession()
    try:
        s.execute(text("ALTER TABLE audit_logs DISABLE TRIGGER ALL;"))
        s.execute(text("DELETE FROM audit_logs;"))
        s.commit()
    except Exception:
        s.rollback()
    finally:
        s.close()

    yield  # <-- aquí corre el test

    s2 = OSession()
    try:
        s2.execute(text("ALTER TABLE audit_logs DISABLE TRIGGER ALL;"))
        s2.execute(text("DELETE FROM audit_logs;"))
        s2.execute(text("ALTER TABLE audit_logs ENABLE TRIGGER ALL;"))
        s2.commit()
    except Exception:
        s2.rollback()
    finally:
        s2.close()
