import sys
from pathlib import Path

# Agregar la carpeta backend al PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.models import Usuario, RolEnum
from app.auth import get_password_hash

def crear_o_actualizar_usuario():
    db = SessionLocal()
    
    correo_prueba = "admin@criptomed.com"
    password_prueba = "Admin123!"
    
    usuario = db.query(Usuario).filter(Usuario.email == correo_prueba).first()
    
    if usuario:
        # Si ya existe, le actualizamos la contraseña por una conocida
        usuario.password_hash = get_password_hash(password_prueba)
        usuario.activo = True
        db.commit()
        print(f"¡Contraseña de {correo_prueba} actualizada con éxito!")
    else:
        # Si no existe, lo creamos de cero
        nuevo_usuario = Usuario(
            nombre="Administrador",
            email=correo_prueba,
            password_hash=get_password_hash(password_prueba),
            rol=RolEnum.admin,
            activo=True
        )
        db.add(nuevo_usuario)
        db.commit()
        print(f"¡Usuario {correo_prueba} creado con éxito!")
        
    print(f"Credenciales listas -> Email: {correo_prueba} | Password: {password_prueba}")
    db.close()

if __name__ == "__main__":
    crear_o_actualizar_usuario()