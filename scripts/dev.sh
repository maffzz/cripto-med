#!/bin/bash
# Script de operación para CriptoMed en Docker
# Uso: ./scripts/dev.sh <comando>

set -e

COMPOSE="docker compose"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CERTS_DIR="$PROJECT_ROOT/certs"
ENV_FILE="$PROJECT_ROOT/.env"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker esté corriendo
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker no está corriendo. Inicia Docker e intenta de nuevo."
        exit 1
    fi
}

# Generar certificados si faltan
ensure_certs() {
    if [ ! -f "$CERTS_DIR/cert.pem" ] || [ ! -f "$CERTS_DIR/key.pem" ]; then
        info "Generando certificados SSL autofirmados..."
        mkdir -p "$CERTS_DIR"
        "$PROJECT_ROOT/scripts/gen_cert.sh"
    else
        info "Certificados SSL ya existen."
    fi
}

# Validar que exista .env
ensure_env() {
    if [ ! -f "$ENV_FILE" ]; then
        error ".env no existe. Ejecuta: python3 scripts/generate_secrets.py --generate-env"
        exit 1
    fi
    info ".env encontrado."
}

# Subcomando: up
cmd_up() {
    check_docker
    ensure_env
    ensure_certs
    info "Construyendo y levantando servicios..."
    cd "$PROJECT_ROOT"
    $COMPOSE build
    $COMPOSE up -d
    info "Servicios levantados. Abre https://localhost:8443 en tu navegador."
}

# Subcomando: seed
cmd_seed() {
    check_docker
    ensure_env
    info "Ejecutando perfil seed (setup_db + seed_db)..."
    cd "$PROJECT_ROOT"
    $COMPOSE --profile seed up init
    info "Datos de ejemplo cargados."
}

# Subcomando: down
cmd_down() {
    info "Deteniendo servicios..."
    cd "$PROJECT_ROOT"
    $COMPOSE down
    info "Servicios detenidos."
}

# Subcomando: reset
cmd_reset() {
    warn "Esto borrará todos los datos (volumen pgdata). ¿Continuar? (s/N)"
    read -r response
    if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
        info "Reiniciando desde cero..."
        cd "$PROJECT_ROOT"
        $COMPOSE down -v
        cmd_up
        cmd_seed
    else
        info "Cancelado."
    fi
}

# Subcomando: logs
cmd_logs() {
    cd "$PROJECT_ROOT"
    $COMPOSE logs -f
}

# Subcomando: ps
cmd_ps() {
    cd "$PROJECT_ROOT"
    $COMPOSE ps
}

# Subcomando: test
cmd_test() {
    check_docker
    ensure_env
    info "Ejecutando pruebas pytest en el contenedor backend..."
    cd "$PROJECT_ROOT"
    $COMPOSE run --rm backend pytest tests/ -v
}

# Subcomando: shell-db
cmd_shell_db() {
    check_docker
    ensure_env
    info "Abriendo psql en el contenedor db..."
    cd "$PROJECT_ROOT"
    $COMPOSE exec db psql -U criptomed -d criptomed
}

# Subcomando: health
cmd_health() {
    info "Verificando health de servicios..."
    cd "$PROJECT_ROOT"
    $COMPOSE ps
    echo ""
    info "Verificando endpoint /health..."
    curl -k -s https://localhost:8443/health || error "Endpoint /health no responde"
}

# Mostrar ayuda
show_help() {
    echo "Uso: $0 <comando>"
    echo ""
    echo "Comandos disponibles:"
    echo "  up       - Genera certs si faltan, valida .env, build y levanta servicios"
    echo "  seed     - Ejecuta el perfil seed (setup_db + seed_db)"
    echo "  down     - Detiene servicios"
    echo "  reset    - Borra todo (volumen pgdata) y reinicia desde cero"
    echo "  logs     - Muestra logs de todos los servicios (follow)"
    echo "  ps       - Muestra estado de contenedores"
    echo "  test     - Ejecuta pytest en el contenedor backend"
    echo "  shell-db - Abre psql en el contenedor db"
    echo "  health   - Verifica health de servicios y endpoint /health"
    echo "  help     - Muestra esta ayuda"
}

# Main
case "${1:-help}" in
    up)
        cmd_up
        ;;
    seed)
        cmd_seed
        ;;
    down)
        cmd_down
        ;;
    reset)
        cmd_reset
        ;;
    logs)
        cmd_logs
        ;;
    ps)
        cmd_ps
        ;;
    test)
        cmd_test
        ;;
    shell-db)
        cmd_shell_db
        ;;
    health)
        cmd_health
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Comando desconocido: $1"
        show_help
        exit 1
        ;;
esac
