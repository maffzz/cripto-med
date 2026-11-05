#!/bin/bash
# Script de demostración: rotación de llaves en vivo
# Muestra la rotación de llaves de cifrado sin interrumpir el servicio

set -e

echo "=== Demo de Rotación de Llaves ==="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Paso 1: Mostrar estado actual de llaves
echo -e "${YELLOW}[1/5] Estado actual de llaves (por versión):${NC}"
docker compose exec -T backend python -c "
import sys
sys.path.insert(0, '/app')
from app.database import SessionLocal
from app.models import Paciente

db = SessionLocal()
try:
    # Contar campos por versión en pacientes
    pacientes = db.query(Paciente).all()
    
    from collections import Counter
    versiones = Counter()
    
    for p in pacientes:
        if p.nombre and p.nombre.startswith('v'):
            version = p.nombre.split(':')[0]
            versiones[version] += 1
        if p.diagnostico and p.diagnostico.startswith('v'):
            version = p.diagnostico.split(':')[0]
            versiones[version] += 1
        if p.medicacion and p.medicacion.startswith('v'):
            version = p.medicacion.split(':')[0]
            versiones[version] += 1
        if p.resultado_test and p.resultado_test.startswith('v'):
            version = p.resultado_test.split(':')[0]
            versiones[version] += 1
        if p.monto_facturado and p.monto_facturado.startswith('v'):
            version = p.monto_facturado.split(':')[0]
            versiones[version] += 1
    
    print('Campos cifrados por versión:')
    for v in sorted(versiones.keys()):
        print(f'  {v}: {versiones[v]} campos')
finally:
    db.close()
"

# Paso 2: Agregar nueva versión de llave y ponerla como actual
echo -e "${YELLOW}[2/5] Agregando nueva versión de llave (v3)...${NC}"

# Leer ENC_KEYS actual
ENC_KEYS=$(grep "^ENC_KEYS=" .env | cut -d'=' -f2-)

# Extraer llaves existentes y agregar v3
# Generar nueva llave de 32 bytes (256 bits) en base64url
NEW_KEY=$(python3 -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8'))")

# Construir nueva ENC_KEYS con v3
if [ -z "$ENC_KEYS" ]; then
    ENC_KEYS="v3:$NEW_KEY"
else
    ENC_KEYS="$ENC_KEYS,v3:$NEW_KEY"
fi

# Actualizar ENC_KEYS en .env
sed -i.bak "s/^ENC_KEYS=.*/ENC_KEYS=$ENC_KEYS/" .env

# Actualizar ENC_KEY_CURRENT a v3
sed -i.bak "s/^ENC_KEY_CURRENT=.*/ENC_KEY_CURRENT=v3/" .env

echo "Nueva llave v3 generada y agregada a ENC_KEYS"
echo "ENC_KEY_CURRENT actualizado a v3"

# Paso 3: Reiniciar backend con nueva configuración
echo -e "${YELLOW}[3/5] Reiniciando backend con nueva ENC_KEY_CURRENT...${NC}"
docker compose up -d backend

# Esperar a que backend esté healthy
echo "Esperando a que backend esté healthy..."
sleep 10

# Paso 4: Ejecutar rotación de llaves
echo -e "${YELLOW}[4/5] Ejecutando rotación de llaves (migrando a v3)...${NC}"
docker compose run --rm backend python scripts/rotate_keys.py --dry-run false

# Paso 5: Mostrar estado después de rotación
echo -e "${YELLOW}[5/5] Estado después de rotación:${NC}"
docker compose exec -T backend python -c "
import sys
sys.path.insert(0, '/app')
from app.database import SessionLocal
from app.models import Paciente

db = SessionLocal()
try:
    pacientes = db.query(Paciente).all()
    
    from collections import Counter
    versiones = Counter()
    
    for p in pacientes:
        if p.nombre and p.nombre.startswith('v'):
            version = p.nombre.split(':')[0]
            versiones[version] += 1
        if p.diagnostico and p.diagnostico.startswith('v'):
            version = p.diagnostico.split(':')[0]
            versiones[version] += 1
        if p.medicacion and p.medicacion.startswith('v'):
            version = p.medicacion.split(':')[0]
            versiones[version] += 1
        if p.resultado_test and p.resultado_test.startswith('v'):
            version = p.resultado_test.split(':')[0]
            versiones[version] += 1
        if p.monto_facturado and p.monto_facturado.startswith('v'):
            version = p.monto_facturado.split(':')[0]
            versiones[version] += 1
    
    print('Campos cifrados por versión (después de rotación):')
    for v in sorted(versiones.keys()):
        print(f'  {v}: {versiones[v]} campos')
    
    print('')
    print('Verificación de rotación:')
    if 'v2' in versiones and versiones['v2'] == 0:
        print(f'  {GREEN}✓ Todos los campos migrados a v3{NC}')
    else:
        print(f'  {RED}✗ Aún hay campos en v2{NC}')
finally:
    db.close()
"

# Paso 6: Verificar que la API funciona con la nueva llave
echo -e "${YELLOW}[6/6] Verificando que la API funciona con la nueva llave...${NC}"

# Login como doctor y verificar que se lean datos
RESPONSE=$(curl -s -X POST https://localhost:8443/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ana.torres@criptomed.local","password":"'$DEMO_PASSWORD_DOCTOR'"}' \
  -k)

if echo "$RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Login exitoso${NC}"
    TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    
    # Obtener pacientes
    PATIENTES=$(curl -s -X GET https://localhost:8443/api/pacientes \
      -H "Authorization: Bearer $TOKEN" \
      -k)
    
    if echo "$PATIENTES" | grep -q "Paciente Demo"; then
        echo -e "${GREEN}✓ Datos legibles con nueva llave v3${NC}"
    else
        echo -e "${RED}✗ Error leyendo datos${NC}"
    fi
else
    echo -e "${RED}✗ Login falló${NC}"
fi

echo ""
echo -e "${GREEN}=== Demo de rotación completada ===${NC}"
echo ""
echo "Para volver al estado inicial (v2):"
echo "  1. Restaurar .env.bak: cp .env.bak .env"
echo "  2. Reiniciar backend: docker compose up -d backend"
echo "  3. Ejecutar rotate_keys.py --dry-run false para migrar de vuelta a v2"
echo "  4. O ejecutar ./scripts/preparar_demo.sh para reset completo"
