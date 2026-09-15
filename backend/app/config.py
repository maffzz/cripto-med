from pathlib import Path # rutas de archivos independientes del sistema

from dotenv import load_dotenv # carga variables desde el archivo .env
import os # lee variables de entorno del sistema

ROOT_DIR = Path(__file__).resolve().parents[2] # raiz del repo (cripto-med)
BACKEND_DIR = Path(__file__).resolve().parents[1] # carpeta backend/

load_dotenv(ROOT_DIR / ".env") # inyecta el .env en os.environ


def _env(name: str, default: str) -> str: # helper para leer una variable con fallback
    return os.getenv(name, default) # si no existe, usa el valor por defecto


DATABASE_URL = _env("DATABASE_URL", "sqlite:///./criptomed.db") # conexion sqlite local
JWT_SECRET = _env("JWT_SECRET", "cambiar-en-local") # secreto para firmar tokens jwt
JWT_ALGORITHM = _env("JWT_ALGORITHM", "HS256") # algoritmo de firma del jwt
JWT_EXPIRE_MINUTES = int(_env("JWT_EXPIRE_MINUTES", "30")) # minutos de vida del token
ENCRYPTION_KEY = _env("ENCRYPTION_KEY", "cambiar-en-local") # llave fernet (aes-256)