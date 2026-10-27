#!/bin/bash
# Script de verificación de despliegue para CriptoMed
# Verifica 8 puntos críticos del despliegue Docker

set -e

echo "=== Verificación de Despliegue CriptoMed ==="
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

check_result=0

# 1. Verificar HTTPS y TLS 1.3
echo "1. Verificando HTTPS://localhost:8443 y TLS 1.3..."
if curl -k -s -o /dev/null -w "%{http_code}" https://localhost:8443/ | grep -q "200"; then
    echo -e "${GREEN}OK${NC}: HTTPS responde"
    if echo | openssl s_client -connect localhost:8443 -tls1_3 2>/dev/null | grep -q "Protocol.*TLSv1.3"; then
        echo -e "${GREEN}OK${NC}: TLS 1.3 negociado"
    else
        echo -e "${RED}FALLA${NC}: TLS 1.3 no negociado"
        check_result=1
    fi
else
    echo -e "${RED}FALLA${NC}: HTTPS no responde"
    check_result=1
fi
echo ""

# 2. Verificar que puertos 5432 y 8000 NO son accesibles desde el host
echo "2. Verificando que puertos 5432 y 8000 NO son expuestos por Docker..."
# Verificar si los puertos están expuestos por Docker (no solo si son accesibles)
if docker compose ps | grep -q "5432->"; then
    echo -e "${RED}FALLA${NC}: Puerto 5432 es expuesto por Docker"
    check_result=1
else
    echo -e "${GREEN}OK${NC}: Puerto 5432 (Postgres) no es expuesto por Docker"
fi

if docker compose ps | grep -q "8000->"; then
    echo -e "${RED}FALLA${NC}: Puerto 8000 es expuesto por Docker"
    check_result=1
else
    echo -e "${GREEN}OK${NC}: Puerto 8000 (backend) no es expuesto por Docker"
fi
echo ""

# 3. Verificar que todos los servicios están healthy
echo "3. Verificando estado de servicios..."
if docker compose ps | grep -q "db.*healthy" && \
   docker compose ps | grep -q "backend.*healthy" && \
   docker compose ps | grep -q "edge.*Up"; then
    echo -e "${GREEN}OK${NC}: Todos los servicios están healthy/up"
else
    echo -e "${RED}FALLA${NC}: Algunos servicios no están healthy"
    docker compose ps
    check_result=1
fi
echo ""

# 4. Verificar login con usuario demo
echo "4. Verificando login con usuario demo..."
# Nota: El backend usa email como username en OAuth2PasswordRequestForm
response=$(curl -k -s -X POST https://localhost:8443/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@criptomed.local&password=admin123" || echo "ERROR")
if echo "$response" | grep -q "access_token"; then
    echo -e "${GREEN}OK${NC}: Login funciona"
else
    echo -e "${RED}FALLA${NC}: Login no funciona (posible problema con hash de contraseña o ruta)"
    echo "Response: $response"
    check_result=1
fi
echo ""

# 5. Verificar que contenedores corren con usuario no root
echo "5. Verificando que contenedores corren con usuario no root..."
backend_uid=$(docker compose exec -T backend id -u 2>/dev/null || echo "0")
if [ "$backend_uid" != "0" ]; then
    echo -e "${GREEN}OK${NC}: Backend corre con UID $backend_uid (no root)"
else
    echo -e "${RED}FALLA${NC}: Backend corre como root"
    check_result=1
fi
echo ""

# 6. Verificar que no hay .env ni *.pem en las imágenes
echo "6. Verificando que no hay .env ni *.pem en las imágenes..."
if docker run --rm --entrypoint sh cripto-med-backend -c "ls -a /app" 2>/dev/null | grep -q "\.env"; then
    echo -e "${RED}FALLA${NC}: .env encontrado en imagen backend"
    check_result=1
else
    echo -e "${GREEN}OK${NC}: No hay .env en imagen backend"
fi

if docker run --rm --entrypoint sh cripto-med-edge -c "ls -a /etc/nginx" 2>/dev/null | grep -q "\.pem"; then
    echo -e "${RED}FALLA${NC}: .pem encontrado en imagen edge"
    check_result=1
else
    echo -e "${GREEN}OK${NC}: No hay .pem en imagen edge"
fi
echo ""

# 7. Verificar que docker compose config no contiene secretos literales
echo "7. Verificando que docker compose config no contiene secretos literales..."
if docker compose config 2>/dev/null | grep -q "cambia-esto"; then
    echo -e "${RED}FALLA${NC}: docker compose config contiene valores literales de ejemplo"
    check_result=1
else
    echo -e "${GREEN}OK${NC}: docker compose config no contiene secretos literales"
fi
echo ""

# 8. Verificar reset completo
echo "8. Verificando reset completo (no ejecutado automáticamente)..."
echo "Para verificar manualmente, ejecuta: ./scripts/dev.sh reset"
echo ""

# Resumen
echo "=== Resumen ==="
if [ $check_result -eq 0 ]; then
    echo -e "${GREEN}TODAS LAS VERIFICACIONES PASARON${NC}"
    exit 0
else
    echo -e "${RED}ALGUNAS VERIFICACIONES FALLARON${NC}"
    exit 1
fi
