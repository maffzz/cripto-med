#!/bin/bash
# Script de operación para CriptoMed en Docker
# Uso: ./scripts/dev.sh <comando>
#
# Flujo completo desde cero:
#   ./scripts/dev.sh deploy   → genera .env, certs, build, up, seed (todo en uno)
#   ./scripts/dev.sh up       → build, up y seed automático
#   ./scripts/dev.sh reset    → borra datos y repite deploy completo

set -euo pipefail

COMPOSE="docker compose"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CERTS_DIR="$PROJECT_ROOT/certs"
ENV_FILE="$PROJECT_ROOT/.env"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }
step()    { echo -e "\n${BOLD}${BLUE}▶ $1${NC}"; }
success() { echo -e "${GREEN}${BOLD}✔ $1${NC}"; }

# ---------------------------------------------------------------------------
# Checks previos
# ---------------------------------------------------------------------------

check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker no está corriendo. Inicia Docker e intenta de nuevo."
        exit 1
    fi
}

check_python() {
    if ! command -v python3 &>/dev/null; then
        error "python3 no encontrado. Instálalo e intenta de nuevo."
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Generación de .env
# ---------------------------------------------------------------------------

ensure_env() {
    if [ ! -f "$ENV_FILE" ]; then
        step "Generando .env con secretos aleatorios..."
        check_python
        python3 "$SCRIPTS_DIR/generate_secrets.py" --generate-env
        success ".env generado"
    else
        info ".env ya existe — se respetan los valores actuales."
    fi
}

# ---------------------------------------------------------------------------
# Generación de certificados TLS
# ---------------------------------------------------------------------------

ensure_certs() {
    if [ ! -f "$CERTS_DIR/cert.pem" ] || [ ! -f "$CERTS_DIR/key.pem" ]; then
        step "Generando certificados TLS autofirmados..."
        mkdir -p "$CERTS_DIR"
        bash "$SCRIPTS_DIR/gen_cert.sh"
        success "Certificados generados en $CERTS_DIR"
    else
        info "Certificados TLS ya existen."
    fi
}

# ---------------------------------------------------------------------------
# Build de imágenes Docker
# ---------------------------------------------------------------------------

cmd_build() {
    step "Construyendo imágenes Docker (backend, edge, init)..."
    cd "$PROJECT_ROOT"
    # Construye todos los servicios definidos, incluido el perfil seed (init)
    $COMPOSE build
    $COMPOSE --profile seed build
    success "Imágenes construidas"
}

# ---------------------------------------------------------------------------
# Levantar servicios base
# ---------------------------------------------------------------------------

cmd_services_up() {
    step "Levantando servicios (db, backend, edge)..."
    cd "$PROJECT_ROOT"
    $COMPOSE up -d
    success "Servicios levantados"
}

# ---------------------------------------------------------------------------
# Esperar a que backend esté healthy antes de hacer seed
# ---------------------------------------------------------------------------

wait_backend_healthy() {
    step "Esperando que backend esté healthy..."
    local max_attempts=30
    local attempt=0
    cd "$PROJECT_ROOT"
    while [ $attempt -lt $max_attempts ]; do
        status=$($COMPOSE ps backend --format json 2>/dev/null | python3 -c "
import sys, json
data = sys.stdin.read().strip()
# docker compose ps puede devolver líneas JSON o array
lines = [l for l in data.splitlines() if l.strip()]
for line in lines:
    try:
        obj = json.loads(line)
        print(obj.get('Health', obj.get('Status', '')))
        break
    except Exception:
        pass
" 2>/dev/null || echo "")

        if echo "$status" | grep -qi "healthy"; then
            success "Backend healthy"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 3
    done
    echo ""
    error "Backend no alcanzó estado healthy tras $((max_attempts * 3))s."
    $COMPOSE logs backend | tail -20
    exit 1
}

# ---------------------------------------------------------------------------
# Seed de base de datos (setup + datos demo)
# ---------------------------------------------------------------------------

cmd_seed() {
    check_docker
    ensure_env
    step "Ejecutando seed (setup_db + seed_db)..."
    cd "$PROJECT_ROOT"
    $COMPOSE --profile seed run --rm init
    success "Base de datos inicializada y datos demo cargados"
}

# ---------------------------------------------------------------------------
# Verificación rápida post-despliegue
# ---------------------------------------------------------------------------

cmd_smoke_test() {
    step "Verificación rápida de login con usuario admin..."
    local admin_pass
    admin_pass=$(grep '^DEMO_PASSWORD_ADMIN=' "$ENV_FILE" | cut -d '=' -f2- | tr -d '"' | tr -d "'")

    if [ -z "$admin_pass" ]; then
        warn "No se encontró DEMO_PASSWORD_ADMIN en .env — omitiendo smoke test de login."
        return 0
    fi

    local response
    # Pequeña espera para que nginx esté listo
    sleep 2
    response=$(curl -k -s -X POST https://localhost:8443/api/auth/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data-urlencode "username=admin@criptomed.com" \
        --data-urlencode "password=${admin_pass}" 2>/dev/null || echo "ERROR")

    if echo "$response" | grep -q "access_token"; then
        success "Login admin OK"
    else
        warn "Smoke test de login falló (respuesta: $response)"
        warn "Verifica que el seed terminó correctamente y que el .env es válido."
    fi
}

# ---------------------------------------------------------------------------
# Subcomando: deploy (flujo completo desde cero)
# ---------------------------------------------------------------------------

cmd_deploy() {
    echo -e "\n${BOLD}${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BOLD}${BLUE}   CriptoMed — Despliegue Completo${NC}"
    echo -e "${BOLD}${BLUE}═══════════════════════════════════════${NC}"

    check_docker
    check_python
    ensure_env
    ensure_certs
    cmd_build
    cmd_services_up
    wait_backend_healthy
    cmd_seed
    cmd_smoke_test

    echo -e "\n${GREEN}${BOLD}═══════════════════════════════════════${NC}"
    success "¡Despliegue completo!"
    echo -e "${GREEN}${BOLD}   https://localhost:8443${NC}"
    echo ""
    echo -e "  Usuarios demo (contraseñas en .env):"
    echo -e "  • admin@criptomed.com        (DEMO_PASSWORD_ADMIN)"
    echo -e "  • doctor@criptomed.com       (DEMO_PASSWORD_DOCTOR)"
    echo -e "  • dr.ramirez@criptomed.com   (DEMO_PASSWORD_DOCTOR)"
    echo -e "  • dra.quispe@criptomed.com   (DEMO_PASSWORD_DOCTOR)"
    echo -e "  • admin@clinica.com          (DEMO_PASSWORD_ADMINISTRATIVO)"
    echo -e "  • auditor@criptomed.com      (DEMO_PASSWORD_AUDITOR)"
    echo -e "  • paciente@criptomed.com     (DEMO_PASSWORD_PACIENTE)"
    echo -e "${GREEN}${BOLD}═══════════════════════════════════════${NC}\n"
}

# ---------------------------------------------------------------------------
# Subcomando: up (build + up + seed automático)
# ---------------------------------------------------------------------------

cmd_up() {
    check_docker
    ensure_env
    ensure_certs
    cmd_build
    cmd_services_up
    wait_backend_healthy
    cmd_seed
    cmd_smoke_test
    info "Servicios listos. Abre https://localhost:8443"
}

# ---------------------------------------------------------------------------
# Subcomando: down
# ---------------------------------------------------------------------------

cmd_down() {
    step "Deteniendo servicios..."
    cd "$PROJECT_ROOT"
    $COMPOSE down
    success "Servicios detenidos"
}

# ---------------------------------------------------------------------------
# Subcomando: reset (borra volúmenes + deploy completo)
# ---------------------------------------------------------------------------

cmd_reset() {
    warn "Esto borrará TODOS los datos (volumen pgdata) y redesplegará desde cero."
    warn "¿Continuar? (s/N)"
    read -r response
    if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
        step "Deteniendo servicios y borrando volúmenes..."
        cd "$PROJECT_ROOT"
        $COMPOSE down -v
        success "Volúmenes eliminados"
        cmd_deploy
    else
        info "Cancelado."
    fi
}

# ---------------------------------------------------------------------------
# Subcomando: logs
# ---------------------------------------------------------------------------

cmd_logs() {
    cd "$PROJECT_ROOT"
    SERVICE="${2:-}"
    if [ -n "$SERVICE" ]; then
        $COMPOSE logs -f "$SERVICE"
    else
        $COMPOSE logs -f
    fi
}

# ---------------------------------------------------------------------------
# Subcomando: ps
# ---------------------------------------------------------------------------

cmd_ps() {
    cd "$PROJECT_ROOT"
    $COMPOSE ps
}

# ---------------------------------------------------------------------------
# Subcomando: test
# ---------------------------------------------------------------------------

cmd_test() {
    check_docker
    ensure_env
    step "Ejecutando pruebas pytest en el contenedor backend..."
    cd "$PROJECT_ROOT"
    $COMPOSE exec backend pytest tests/ -v -p no:cacheprovider
}

# ---------------------------------------------------------------------------
# Subcomando: shell-db
# ---------------------------------------------------------------------------

cmd_shell_db() {
    check_docker
    ensure_env
    info "Abriendo psql en el contenedor db..."
    cd "$PROJECT_ROOT"
    $COMPOSE exec db psql -U criptomed -d criptomed
}

# ---------------------------------------------------------------------------
# Subcomando: health
# ---------------------------------------------------------------------------

cmd_health() {
    step "Verificando estado de servicios..."
    cd "$PROJECT_ROOT"
    $COMPOSE ps
    echo ""
    info "Verificando endpoint /health..."
    curl -k -s https://localhost:8443/health && echo "" || error "Endpoint /health no responde"
}

# ---------------------------------------------------------------------------
# Ayuda
# ---------------------------------------------------------------------------

show_help() {
    echo ""
    echo -e "${BOLD}Uso:${NC} $0 <comando>"
    echo ""
    echo -e "${BOLD}Comandos principales:${NC}"
    echo "  deploy   - Flujo completo desde cero: .env, certs, build, up, seed, smoke test"
    echo "  up       - Build, levanta servicios y hace seed automático"
    echo "  seed     - Solo re-ejecuta el seed (rehashea contraseñas del .env actual)"
    echo "  reset    - Borra volúmenes y repite deploy completo (pide confirmación)"
    echo "  down     - Detiene y elimina contenedores"
    echo ""
    echo -e "${BOLD}Operación:${NC}"
    echo "  logs [servicio] - Muestra logs (todos o de un servicio específico)"
    echo "  ps              - Muestra estado de contenedores"
    echo "  health          - Verifica health de servicios y endpoint /health"
    echo "  test            - Ejecuta pytest en el contenedor backend"
    echo "  shell-db        - Abre psql en el contenedor db"
    echo "  help            - Muestra esta ayuda"
    echo ""
    echo -e "${BOLD}Ejemplo de primer despliegue:${NC}"
    echo "  ./scripts/dev.sh deploy"
    echo ""
    echo -e "${BOLD}Si solo cambiaste el .env y quieres rehashear contraseñas:${NC}"
    echo "  ./scripts/dev.sh seed"
    echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

case "${1:-help}" in
    deploy)   cmd_deploy ;;
    up)       cmd_up ;;
    seed)     cmd_seed ;;
    down)     cmd_down ;;
    reset)    cmd_reset ;;
    logs)     cmd_logs "$@" ;;
    ps)       cmd_ps ;;
    test)     cmd_test ;;
    shell-db) cmd_shell_db ;;
    health)   cmd_health ;;
    help|--help|-h) show_help ;;
    *)
        error "Comando desconocido: $1"
        show_help
        exit 1
        ;;
esac
