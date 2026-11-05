#!/bin/bash
# Script de preparación de la demo de CriptoMed
# Deja el sistema en un estado conocido para la demostración en vivo

set -e

echo "=== Preparando demo de CriptoMed ==="
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paso 1: Down con volúmenes
echo -e "${YELLOW}[1/7] Deteniendo servicios y limpiando volúmenes...${NC}"
docker compose down -v

# Paso 2: Levantar con build
echo -e "${YELLOW}[2/7] Levantando servicios con build...${NC}"
docker compose up -d --build

# Paso 3: Esperar a que los servicios estén healthy
echo -e "${YELLOW}[3/7] Esperando a que los servicios estén healthy...${NC}"
echo "Esto puede tomar hasta 60 segundos..."

# Función para verificar healthcheck
wait_for_healthy() {
    local service=$1
    local max_attempts=60
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if docker compose ps $service | grep -q "healthy"; then
            echo -e "${GREEN}✓ $service está healthy${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done

    echo -e "${RED}✗ $service no llegó a healthy${NC}"
    return 1
}

wait_for_healthy db
wait_for_healthy backend
wait_for_healthy edge

# Paso 4: Sembrar datos con las llaves actuales
echo -e "${YELLOW}[4/7] Sembrando datos de demo...${NC}"
# El servicio init con perfil seed ya hace esto automáticamente al levantar
# Pero esperamos a que termine
docker compose logs init | tail -20

# Paso 5: Crear usuarios específicos para la demo
echo -e "${YELLOW}[5/7] Creando usuarios de demo...${NC}"

# Verificar que las variables de entorno estén definidas
if [ -z "$DEMO_PASSWORD_ADMIN" ] || [ -z "$DEMO_PASSWORD_DOCTOR" ] || [ -z "$DEMO_PASSWORD_ADMINISTRATIVO" ] || [ -z "$DEMO_PASSWORD_AUDITOR" ] || [ -z "$DEMO_PASSWORD_PACIENTE" ]; then
    echo -e "${RED}Error: Las variables de entorno DEMO_PASSWORD_* no están definidas${NC}"
    echo "Por favor, configura las variables en .env"
    exit 1
fi

# Función para crear usuario
create_user() {
    local email=$1
    local nombre=$2
    local rol=$3
    local password=$4

    docker compose exec -T backend python -c "
import sys
sys.path.insert(0, '/app')
from app.database import SessionLocal
from app.models import Usuario
from app.auth import get_password_hash

db = SessionLocal()
try:
    # Verificar si el usuario ya existe
    existing = db.query(Usuario).filter(Usuario.email == '$email').first()
    if existing:
        existing.nombre = '$nombre'
        existing.rol = '$rol'
        existing.password_hash = get_password_hash('$password')
        existing.activo = True
        existing.intentos_fallidos = 0
        existing.bloqueado_hasta = None
        print('Usuario actualizado: $email')
    else:
        user = Usuario(
            nombre='$nombre',
            email='$email',
            password_hash=get_password_hash('$password'),
            rol='$rol',
            activo=True,
            intentos_fallidos=0,
            bloqueado_hasta=None
        )
        db.add(user)
        print('Usuario creado: $email')
    db.commit()
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
"
}

# Crear doctores
create_user "ana.torres@criptomed.local" "Dra. Ana Torres" "doctor" "$DEMO_PASSWORD_DOCTOR"
create_user "luis.ramirez@criptomed.local" "Dr. Luis Ramírez" "doctor" "$DEMO_PASSWORD_DOCTOR"
create_user "carla.quispe@criptomed.local" "Dra. Carla Quispe" "doctor" "$DEMO_PASSWORD_DOCTOR"

# Crear administrativo
create_user "admin1@criptomed.local" "Admin Demo" "administrativo" "$DEMO_PASSWORD_ADMINISTRATIVO"

# Crear auditor
create_user "auditor1@criptomed.local" "Auditor Demo" "auditor" "$DEMO_PASSWORD_AUDITOR"

# Crear admin (ya existe en seed, pero actualizamos)
create_user "admin@criptomed.local" "Admin Principal" "admin" "$DEMO_PASSWORD_ADMIN"

# Crear paciente demo
create_user "paciente1@criptomed.local" "Paciente Demo" "paciente" "$DEMO_PASSWORD_PACIENTE"

# Paso 6: Asignar Paciente Demo a Dra. Ana Torres con consentimiento
echo -e "${YELLOW}[6/7] Asignando Paciente Demo a Dra. Ana Torres...${NC}"

docker compose exec -T backend python -c "
import sys
sys.path.insert(0, '/app')
from app.database import SessionLocal
from app.models import Usuario, Paciente
from datetime import datetime, timedelta

db = SessionLocal()
try:
    # Obtener IDs
    paciente_usuario = db.query(Usuario).filter(Usuario.email == 'paciente1@criptomed.local').first()
    doctor_ana = db.query(Usuario).filter(Usuario.email == 'ana.torres@criptomed.local').first()
    
    if not paciente_usuario or not doctor_ana:
        print('Error: No se encontraron usuario paciente o doctor')
        sys.exit(1)
    
    # Buscar o crear paciente demo
    paciente = db.query(Paciente).filter(Paciente.usuario_id == paciente_usuario.id).first()
    
    if not paciente:
        # Crear paciente demo con datos
        from app.crypto import encrypt
        
        paciente = Paciente(
            nombre=encrypt('Paciente Demo', aad='pacientes.nombre.tmp'),
            edad=35,
            genero='F',
            tipo_sangre='A+',
            diagnostico=encrypt('Hipertensión arterial', aad='pacientes.diagnostico.tmp'),
            codigo_cie10='I10',
            fecha_admision=datetime.utcnow() - timedelta(days=7),
            doctor_id=doctor_ana.id,
            usuario_id=paciente_usuario.id,
            hospital='Clínica Demo',
            proveedor_seguro='Pacifico Salud',
            monto_facturado=encrypt('1500.00', aad='pacientes.monto_facturado.tmp'),
            numero_habitacion='201',
            tipo_admision='Programada',
            fecha_alta=None,
            medicacion=encrypt('Losartán 50mg', aad='pacientes.medicacion.tmp'),
            resultado_test=encrypt('Normal', aad='pacientes.resultado_test.tmp'),
            consentimiento_fecha=datetime.utcnow(),
            consentimiento_version='v1.0'
        )
        db.add(paciente)
        print('Paciente demo creado')
    else:
        # Actualizar asignación
        paciente.doctor_id = doctor_ana.id
        paciente.consentimiento_fecha = datetime.utcnow()
        paciente.consentimiento_version = 'v1.0'
        print('Paciente demo actualizado')
    
    db.commit()
    print('Paciente Demo asignado a Dra. Ana Torres con consentimiento')
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
"

# Paso 7: Verificaciones
echo -e "${YELLOW}[7/7] Ejecutando verificaciones...${NC}"

# Verificar cadena de logs
echo -n "Verificando cadena de logs... "
if docker compose run --rm backend python scripts/verificar_cadena_logs.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FALLA${NC}"
fi

# Verificar cifrado
echo -n "Verificando cifrado... "
if docker compose run --rm backend python scripts/verificar_cifrado.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FALLA${NC}"
fi

# Verificar despliegue
echo -n "Verificando despliegue... "
if ./scripts/verificar_despliegue.sh > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FALLA${NC}"
fi

# Imprimir tabla de usuarios
echo ""
echo -e "${GREEN}=== Usuarios de demo ===${NC}"
printf "%-40s %-20s %-35s\n" "Usuario" "Rol" "Email"
echo "----------------------------------------------------------------------------------------"

docker compose exec -T backend python -c "
import sys
sys.path.insert(0, '/app')
from app.database import SessionLocal
from app.models import Usuario

db = SessionLocal()
try:
    usuarios = db.query(Usuario).filter(
        Usuario.email.in_([
            'admin@criptomed.local',
            'ana.torres@criptomed.local',
            'luis.ramirez@criptomed.local',
            'carla.quispe@criptomed.local',
            'admin1@criptomed.local',
            'auditor1@criptomed.local',
            'paciente1@criptomed.local'
        ])
    ).order_by(Usuario.rol, Usuario.nombre)
    
    for u in usuarios:
        print(f'{u.nombre:<40} {u.rol.value:<20} {u.email:<35}')
finally:
    db.close()
"

echo ""
echo -e "${GREEN}=== Demo preparada ===${NC}"
echo "Aplicación disponible en: https://localhost:8443"
echo ""
echo "Usuarios de demo:"
echo "  - admin@criptomed.local (admin)"
echo "  - ana.torres@criptomed.local (doctor - Dra. Ana Torres)"
echo "  - luis.ramirez@criptomed.local (doctor - Dr. Luis Ramírez)"
echo "  - carla.quispe@criptomed.local (doctor - Dra. Carla Quispe)"
echo "  - admin1@criptomed.local (administrativo)"
echo "  - auditor1@criptomed.local (auditor)"
echo "  - paciente1@criptomed.local (paciente - asignado a Dra. Ana Torres)"
echo ""
echo "Contraseña para todos: [DEMO_PASSWORD_* del .env]"
