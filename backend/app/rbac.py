from typing import Union, List
from fastapi import Depends, HTTPException, status
from app.models import Usuario, RolEnum, Paciente
from app.auth import get_current_user

# --- 1. Decorador / Dependencia de Roles ---

def require_role(*roles):
    """
    Verifica si el usuario tiene un rol permitido antes de ejecutar el endpoint.
    """
    # Desempaqueta y aplana si el argumento recibido fue una lista
    roles_permitidos = []
    for r in roles:
        if isinstance(r, (list, tuple)):
            roles_permitidos.extend(r)
        else:
            roles_permitidos.append(r)

    def role_checker(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        # Extrae los valores en string para comparar con seguridad
        roles_values = [r.value if hasattr(r, 'value') else str(r) for r in roles_permitidos]
        user_rol_value = usuario.rol.value if hasattr(usuario.rol, 'value') else str(usuario.rol)

        if user_rol_value not in roles_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los siguientes roles: {roles_values}"
            )
        return usuario

    return role_checker


# --- 2. Función de control de permisos ---

def check_permission(usuario: Usuario, accion: str, recurso: any) -> bool:
    """
    Verifica si un usuario puede realizar una acción sobre un recurso específico,
    aplicando el principio de mínimo privilegio.
    """
    # Lógica: admin -> todo
    if usuario.rol == RolEnum.admin:
        return True
        
    # Lógica: auditor -> solo logs
    if usuario.rol == RolEnum.auditor:
        return recurso == "logs" and accion == "lectura"
        
    # Lógica: doctor -> pacientes asignados (diagnóstico completo)
    if usuario.rol == RolEnum.doctor:
        if isinstance(recurso, Paciente):
            # Valida que el paciente pertenezca a este doctor
            return recurso.doctor_id == usuario.id
        # Permite acceso general a la ruta de pacientes (la query en el endpoint filtrará el resto)
        return recurso == "pacientes"
        
    # Lógica: administrativo -> datos básicos + facturación (sin diagnóstico)
    if usuario.rol == RolEnum.administrativo:
        # Aquí restringimos qué "tipo" de recurso puede consultar
        if accion in ["lectura", "edicion"]:
            return recurso in ["pacientes_basico", "facturacion"]
        return False

    # Lógica: paciente -> solo su propio historial y transferir doctor
    if usuario.rol == RolEnum.paciente:
        if isinstance(recurso, Paciente):
            # Valida que el paciente sea el propio usuario
            return recurso.usuario_id == usuario.id
        # Permite acceso a su propio historial
        return recurso == "mi_historial" or recurso == "transferir_doctor"

    return False