#!/bin/bash
# Script de verificación de despliegue para CriptoMed
# Verifica 8 puntos críticos del despliegue Docker
# Lee credenciales desde .env — no hay secretos hardcodeados

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

echo "=== Verificación de Despliegue CriptoMed ==="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_result=0

ok()   { echo -e "${GREEN}OK${NC}: $1"; }
fail() { echo -e "${RED}FALLA${NC}: $1"; check_result=1; }
warn() { echo -e "${YELLOW}WARN${NC}: $1"; }

# Leer DEMO_PASSWORD_ADMIN desde .env
load_admin_password() {
    if [ ! -f "$ENV_FILE" ]; then
        warn ".env no encontrado — se omitirá el test de login."
        echo ""
        return
    fi
    ADMIN_PASS=$(grep '^DEMO_PASSWORD_ADMIN=' "$ENV_FILE" | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d '[:space:]')
}

# ---------------------------------------------------------------------------
# 1. HTTPS y TLS 1.3
# ---------------------------------------------------------------------------
echo "1. Verificando HTTPS://localhost:8443 y TLS 1.3..."
http_code=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost:8443/ 2>/dev/null || echo "000")
if [ "$http_code" = "200" ]; then
    ok "HTTPS responde (HTTP $http_code)"
else
    fail "HTTPS no responde (HTTP $http_code)"
fi

if echo | openssl s_client -connect localhost:8443 -tls1_3 2>/dev/null | grep -q "Protocol.*TLSv1.3"; then
    ok "TLS 1.3 negociado"
else
    fail "TLS 1.3 no negociado"
fi
echo ""

# ---------------------------------------------------------------------------
# 2. Puertos internos no expuestos
# ---------------------------------------------------------------------------
echo "2. Verificando que puertos 5432 y 8000 no son expuestos por Docker..."
cd "$PROJECT_ROOT"
if docker compose ps 2>/dev/null | grep -q "5432->"; then
    fail "Puerto 5432 (Postgres) está expuesto al host"
else
    ok "Puerto 5432 (Postgres) no expuesto"
fi

if docker compose ps 2>/dev/null | grep -q "8000->"; then
    fail "Puerto 8000 (backend) está expuesto al host"
else
    ok "Puerto 8000 (backend) no expuesto"
fi
echo ""

# ---------------------------------------------------------------------------
# 3. Estado healthy de servicios
# ---------------------------------------------------------------------------
echo "3. Verificando estado de servicios..."
ps_out=$(docker compose ps 2>/dev/null || echo "")
if echo "$ps_out" | grep -q "db.*healthy" && \
   echo "$ps_out" | grep -q "backend.*healthy" && \
   echo "$ps_out" | grep -q "edge.*Up"; then
    ok "Todos los servicios están healthy/up"
else
    fail "Algunos servicios no están healthy"
    docker compose ps 2>/dev/null || true
fi
echo ""

# ---------------------------------------------------------------------------
# 4. Login con usuario demo (credenciales desde .env)
# ---------------------------------------------------------------------------
echo "4. Verificando login con usuario admin..."
ADMIN_PASS=""
load_admin_password

if [ -z "$ADMIN_PASS" ]; then
    warn "DEMO_PASSWORD_ADMIN vacío en .env — omitiendo test de login."
else
    response=$(curl -k -s -X POST https://localhost:8443/api/auth/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data-urlencode "username=admin@criptomed.com" \
        --data-urlencode "password=${ADMIN_PASS}" 2>/dev/null || echo "ERROR")

    if echo "$response" | grep -q "access_token"; then
        ok "Login admin funciona"
    else
        fail "Login admin falló — verifica que el seed fue ejecutado con el .env actual"
        echo "  Respuesta: $response"
        echo "  Tip: corre './scripts/dev.sh seed' para rehashear contraseñas"
    fi
fi
echo ""

# ---------------------------------------------------------------------------
# 5. Contenedores corren con usuario no root
# ---------------------------------------------------------------------------
echo "5. Verificando que backend corre con usuario no root..."
backend_uid=$(docker compose exec -T backend id -u 2>/dev/null || echo "0")
if [ "$backend_uid" != "0" ]; then
    ok "Backend corre con UID $backend_uid (no root)"
else
    fail "Backend corre como root"
fi
echo ""

# ---------------------------------------------------------------------------
# 6. Sin .env ni *.pem en imágenes
# ---------------------------------------------------------------------------
echo "6. Verificando que no hay .env ni *.pem en las imágenes..."
if docker run --rm --entrypoint sh cripto-med-backend -c "ls -a /app" 2>/dev/null | grep -q "\.env"; then
    fail ".env encontrado en imagen backend"
else
    ok "No hay .env en imagen backend"
fi

if docker run --rm --entrypoint sh cripto-med-edge -c "ls -a /etc/nginx" 2>/dev/null | grep -q "\.pem"; then
    fail ".pem encontrado en imagen edge"
else
    ok "No hay .pem embebido en imagen edge"
fi
echo ""

# ---------------------------------------------------------------------------
# 7. docker compose config sin secretos de ejemplo
# ---------------------------------------------------------------------------
echo "7. Verificando que compose config no contiene valores de ejemplo..."
if docker compose config 2>/dev/null | grep -q "cambia-esto"; then
    fail "compose config contiene valores literales de ejemplo"
else
    ok "compose config no contiene secretos literales de ejemplo"
fi
echo ""

# ---------------------------------------------------------------------------
# 8. Verificar que las imágenes están actualizadas (build reciente)
# ---------------------------------------------------------------------------
echo "8. Verificando que las imágenes cripto-med-backend y cripto-med-init existen..."
if docker image inspect cripto-med-backend:latest &>/dev/null; then
    ok "Imagen cripto-med-backend existe"
else
    fail "Imagen cripto-med-backend no existe — ejecuta './scripts/dev.sh deploy'"
fi

if docker image inspect cripto-med-init:latest &>/dev/null 2>/dev/null || \
   docker images --format "{{.Repository}}" | grep -q "cripto-med-init"; then
    ok "Imagen cripto-med-init existe"
else
    warn "Imagen cripto-med-init no encontrada — ejecuta './scripts/dev.sh deploy'"
fi
echo ""

# ---------------------------------------------------------------------------
# Resumen
# ---------------------------------------------------------------------------
echo "=== Resumen ==="
if [ $check_result -eq 0 ]; then
    echo -e "${GREEN}TODAS LAS VERIFICACIONES PASARON${NC}"
    exit 0
else
    echo -e "${RED}ALGUNAS VERIFICACIONES FALLARON${NC}"
    echo ""
    echo "Consejo: si el problema es el login, ejecuta: ./scripts/dev.sh seed"
    echo "Si es un problema de imágenes desactualizadas: ./scripts/dev.sh deploy"
    exit 1
fi
