from pathlib import Path
from dotenv import load_dotenv
import os

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")

def _env(name: str, default: str) -> str:
    return os.getenv(name, default)

DATABASE_URL = _env("DATABASE_URL", "sqlite:///./criptomed.db")
JWT_SECRET = _env("JWT_SECRET", "cambiar-en-local")
JWT_ALGORITHM = _env("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(_env("JWT_EXPIRE_MINUTES", "30"))

# Cifrado AES-256-GCM (NIST SP 800-38D / FIPS 197)
ENC_KEYS = _env("ENC_KEYS", "")
ENC_KEY_CURRENT = _env("ENC_KEY_CURRENT", "")

# Configuración de Entorno y Seguridad HTTP / CORS (OWASP)
ENV = _env("ENV", "development").lower()
ALLOWED_ORIGINS_RAW = _env("ALLOWED_ORIGINS", "https://localhost:8443,http://localhost:5173")
ALLOWED_ORIGINS = [orig.strip() for orig in ALLOWED_ORIGINS_RAW.split(",") if orig.strip()]

