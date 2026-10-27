# Script de operación para CriptoMed en Docker (PowerShell)
# Uso: .\scripts\dev.ps1 <comando>

$ErrorActionPreference = "Stop"

$COMPOSE = "docker compose"
$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$CERTS_DIR = Join-Path $PROJECT_ROOT "certs"
$ENV_FILE = Join-Path $PROJECT_ROOT ".env"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Verificar que Docker esté corriendo
function Test-Docker {
    try {
        docker info > $null 2>&1
    } catch {
        Write-Error "Docker no está corriendo. Inicia Docker e intenta de nuevo."
        exit 1
    }
}

# Generar certificados si faltan
function Ensure-Certs {
    if (-not (Test-Path "$CERTS_DIR\cert.pem") -or -not (Test-Path "$CERTS_DIR\key.pem")) {
        Write-Info "Generando certificados SSL autofirmados..."
        New-Item -ItemType Directory -Force -Path $CERTS_DIR > $null
        Push-Location $PROJECT_ROOT
        try {
            openssl req -x509 -newkey rsa:2048 -nodes `
                -keyout "$CERTS_DIR\key.pem" `
                -out "$CERTS_DIR\cert.pem" `
                -days 365 `
                -subj "/CN=localhost" `
                -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
        } finally {
            Pop-Location
        }
    } else {
        Write-Info "Certificados SSL ya existen."
    }
}

# Validar que exista .env
function Test-Env {
    if (-not (Test-Path $ENV_FILE)) {
        Write-Error ".env no existe. Ejecuta: python3 scripts\generate_secrets.py --generate-env"
        exit 1
    }
    Write-Info ".env encontrado."
}

# Subcomando: up
function Cmd-Up {
    Test-Docker
    Test-Env
    Ensure-Certs
    Write-Info "Construyendo y levantando servicios..."
    Push-Location $PROJECT_ROOT
    try {
        docker compose build
        docker compose up -d
        Write-Info "Servicios levantados. Abre https://localhost:8443 en tu navegador."
    } finally {
        Pop-Location
    }
}

# Subcomando: seed
function Cmd-Seed {
    Test-Docker
    Test-Env
    Write-Info "Ejecutando perfil seed (setup_db + seed_db)..."
    Push-Location $PROJECT_ROOT
    try {
        docker compose --profile seed up init
        Write-Info "Datos de ejemplo cargados."
    } finally {
        Pop-Location
    }
}

# Subcomando: down
function Cmd-Down {
    Write-Info "Deteniendo servicios..."
    Push-Location $PROJECT_ROOT
    try {
        docker compose down
        Write-Info "Servicios detenidos."
    } finally {
        Pop-Location
    }
}

# Subcomando: reset
function Cmd-Reset {
    $response = Read-Host "Esto borrará todos los datos (volumen pgdata). ¿Continuar? (s/N)"
    if ($response -eq 's' -or $response -eq 'S') {
        Write-Info "Reiniciando desde cero..."
        Push-Location $PROJECT_ROOT
        try {
            docker compose down -v
            Cmd-Up
            Cmd-Seed
        } finally {
            Pop-Location
        }
    } else {
        Write-Info "Cancelado."
    }
}

# Subcomando: logs
function Cmd-Logs {
    Push-Location $PROJECT_ROOT
    try {
        docker compose logs -f
    } finally {
        Pop-Location
    }
}

# Subcomando: ps
function Cmd-Ps {
    Push-Location $PROJECT_ROOT
    try {
        docker compose ps
    } finally {
        Pop-Location
    }
}

# Subcomando: test
function Cmd-Test {
    Test-Docker
    Test-Env
    Write-Info "Ejecutando pruebas pytest en el contenedor backend..."
    Push-Location $PROJECT_ROOT
    try {
        docker compose run --rm backend pytest tests/ -v
    } finally {
        Pop-Location
    }
}

# Subcomando: shell-db
function Cmd-ShellDb {
    Test-Docker
    Test-Env
    Write-Info "Abriendo psql en el contenedor db..."
    Push-Location $PROJECT_ROOT
    try {
        docker compose exec db psql -U criptomed -d criptomed
    } finally {
        Pop-Location
    }
}

# Subcomando: health
function Cmd-Health {
    Write-Info "Verificando health de servicios..."
    Push-Location $PROJECT_ROOT
    try {
        docker compose ps
        Write-Host ""
        Write-Info "Verificando endpoint /health..."
        try {
            curl -k -s https://localhost:8443/health
        } catch {
            Write-Error "Endpoint /health no responde"
        }
    } finally {
        Pop-Location
    }
}

# Mostrar ayuda
function Show-Help {
    Write-Host "Uso: .\scripts\dev.ps1 <comando>"
    Write-Host ""
    Write-Host "Comandos disponibles:"
    Write-Host "  up       - Genera certs si faltan, valida .env, build y levanta servicios"
    Write-Host "  seed     - Ejecuta el perfil seed (setup_db + seed_db)"
    Write-Host "  down     - Detiene servicios"
    Write-Host "  reset    - Borra todo (volumen pgdata) y reinicia desde cero"
    Write-Host "  logs     - Muestra logs de todos los servicios (follow)"
    Write-Host "  ps       - Muestra estado de contenedores"
    Write-Host "  test     - Ejecuta pytest en el contenedor backend"
    Write-Host "  shell-db - Abre psql en el contenedor db"
    Write-Host "  health   - Verifica health de servicios y endpoint /health"
    Write-Host "  help     - Muestra esta ayuda"
}

# Main
$command = if ($args.Count -gt 0) { $args[0] } else { "help" }

switch ($command) {
    "up" { Cmd-Up }
    "seed" { Cmd-Seed }
    "down" { Cmd-Down }
    "reset" { Cmd-Reset }
    "logs" { Cmd-Logs }
    "ps" { Cmd-Ps }
    "test" { Cmd-Test }
    "shell-db" { Cmd-ShellDb }
    "health" { Cmd-Health }
    "help" { Show-Help }
    default {
        Write-Error "Comando desconocido: $command"
        Show-Help
        exit 1
    }
}
