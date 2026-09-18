import sys
from pathlib import Path

# Configurar el path para poder importar los módulos de 'app'
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.models import AuditLog

def verificar_logs():
    db = SessionLocal()
    # Traemos los 5 registros más recientes
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(5).all()
    
    print("\n=== ÚLTIMOS REGISTROS DE AUDITORÍA EN BD ===")
    if not logs:
        print("No hay registros de auditoría aún. Ve a Swagger y haz una petición primero.")
    
    for l in logs:
        usuario = str(l.usuario_id) if l.usuario_id else "Anónimo"
        
        # Extraemos el texto del Enum de forma segura
        accion_str = l.accion.value if hasattr(l.accion, 'value') else str(l.accion)
        
        print(f"[{l.timestamp}] Acción: {accion_str.upper()} | Recurso: {l.recurso}")
        print(f"  -> Usuario ID: {usuario} | IP: {l.ip_origen}")
        print("-" * 65)
        
    db.close()

if __name__ == "__main__":
    verificar_logs()