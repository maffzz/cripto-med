#!/usr/bin/env bash
# ==============================================================================
# scripts/security_scan.sh
# Suite automatizada de escaneo de seguridad multi-herramienta (Fase 2).
# Ejecuta Bandit, pip-audit, npm audit, Gitleaks, Hadolint, Trivy, testssl.sh y ZAP
# completamente dentro de contenedores Docker sin requerir binarios en el host.
# ==============================================================================

set -u

TARGET="${1:-before}"

if [ "$TARGET" != "before" ] && [ "$TARGET" != "after" ]; then
    echo "Uso: $0 [before|after]"
    exit 1
fi

REPORT_DIR="reports/$TARGET"
mkdir -p "$REPORT_DIR"

echo "================================================================================"
echo "    INICIANDO ESCANEO DE SEGURIDAD MULTI-HERRAMIENTA: $TARGET"
echo "    Destino de reportes: $REPORT_DIR/"
echo "================================================================================"

# Asegurar que los servicios base de Docker estén arriba y la red exista
echo "[*] Verificando estado de contenedores base..."
docker compose up -d db backend edge >/dev/null 2>&1

# Habilitar temporalmente ENV=development para exponer /openapi.json a OWASP ZAP
if [ -f "docker-compose.scan.yml" ]; then
    echo "[*] Aplicando docker-compose.scan.yml para habilitar /openapi.json..."
    docker compose -f docker-compose.yml -f docker-compose.scan.yml up -d backend >/dev/null 2>&1
    sleep 3
fi

# Generar token JWT de prueba para endpoints protegidos
echo "[*] Generando token de prueba para análisis autenticado..."
AUTH_TOKEN=$(docker compose run --rm backend python -c "from app.auth import create_access_token; print(create_access_token({'sub': 'doctor@criptomed.com'}))" 2>/dev/null | tr -d '\r\n')

# ------------------------------------------------------------------------------
# 1. Bandit (SAST sobre código Python)
# ------------------------------------------------------------------------------
echo ""
echo ">>> [1/8] SAST: Ejecutando Bandit sobre backend/app y backend/scripts..."
docker run --rm \
  -v "$(pwd)":/src \
  -w /src \
  python:3.12-slim \
  sh -c "pip install --no-cache-dir bandit >/dev/null 2>&1 && bandit -r backend/app backend/scripts -f json -o /src/$REPORT_DIR/bandit.json; bandit -r backend/app backend/scripts -f html -o /src/$REPORT_DIR/bandit.html" || true

# ------------------------------------------------------------------------------
# 2. pip-audit (Vulnerabilidades en dependencias Python)
# ------------------------------------------------------------------------------
echo ""
echo ">>> [2/8] SCA: Ejecutando pip-audit sobre backend/requirements.txt..."
docker run --rm \
  -v "$(pwd)":/src \
  -w /src \
  python:3.12-slim \
  sh -c "pip install --no-cache-dir pip-audit >/dev/null 2>&1 && pip-audit -r backend/requirements.txt -f json -o /src/$REPORT_DIR/pip-audit.json" || true

# ------------------------------------------------------------------------------
# 3. npm audit (Vulnerabilidades en frontend)
# ------------------------------------------------------------------------------
echo ""
echo ">>> [3/8] SCA: Ejecutando npm audit sobre frontend/..."
docker run --rm \
  -v "$(pwd)":/repo \
  -w /repo/frontend \
  node:20-alpine \
  sh -c "npm audit --json > /repo/$REPORT_DIR/npm-audit.json 2>&1" || true

# ------------------------------------------------------------------------------
# 4. Gitleaks (Detección de secretos en repositorio e historial)
# ------------------------------------------------------------------------------
echo ""
echo ">>> [4/8] SECRETOS: Ejecutando Gitleaks sobre todo el repositorio e historial..."
docker run --rm \
  -v "$(pwd)":/repo \
  zricethezav/gitleaks:latest \
  detect --source=/repo --report-format=json --report-path=/repo/$REPORT_DIR/gitleaks.json --no-banner --verbose || true

# ------------------------------------------------------------------------------
# 5. Hadolint (Buenas prácticas de Dockerfiles)
# ------------------------------------------------------------------------------
echo ""
echo ">>> [5/8] LINT: Ejecutando Hadolint sobre Dockerfiles..."
docker run --rm \
  -v "$(pwd)":/work \
  -w /work \
  hadolint/hadolint:latest-alpine \
  hadolint -f json docker/backend/Dockerfile docker/edge/Dockerfile docker/backup/Dockerfile > "$REPORT_DIR/hadolint.json" 2>&1 || true

# ------------------------------------------------------------------------------
# 6. Trivy (Escaneo de vulnerabilidades en filesystem e imágenes construidas)
# ------------------------------------------------------------------------------
echo ""
echo ">>> [6/8] VULNERABILIDADES: Ejecutando Trivy (Filesystem e imágenes Docker)..."
docker run --rm \
  -v "$(pwd)":/work \
  aquasec/trivy:latest \
  fs --format json -o /work/$REPORT_DIR/trivy-fs.json /work || true

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$(pwd)":/work \
  aquasec/trivy:latest \
  image --format json -o /work/$REPORT_DIR/trivy-backend.json cripto-med-backend:latest || true

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$(pwd)":/work \
  aquasec/trivy:latest \
  image --format json -o /work/$REPORT_DIR/trivy-edge.json cripto-med-edge:latest || true

# ------------------------------------------------------------------------------
# 7. testssl.sh (Análisis profundo de TLS 1.3 en edge:8443)
# ------------------------------------------------------------------------------
echo ""
echo ">>> [7/8] TLS: Ejecutando testssl.sh contra https://edge:8443 desde la red interna..."
rm -f "$REPORT_DIR"/testssl.* 2>/dev/null || true
docker run --rm \
  --network cripto-med_app_net \
  -v "$(pwd)/$REPORT_DIR":/reports \
  drwetter/testssl.sh:latest \
  --overwrite \
  --jsonfile /reports/testssl.json \
  --htmlfile /reports/testssl.html \
  --quiet --warnings off \
  https://edge:8443 || true

# ------------------------------------------------------------------------------
# 8. OWASP ZAP (Baseline y API Scan DAST)
# ------------------------------------------------------------------------------
echo ""
echo ">>> [8/8] DAST: Ejecutando OWASP ZAP (Baseline y API Scan)..."
docker run --rm \
  --network cripto-med_app_net \
  -v "$(pwd)/$REPORT_DIR":/zap/wrk/:rw \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://backend:8000 \
  -J zap-baseline.json -r zap-baseline.html -I || true

docker run --rm \
  --network cripto-med_app_net \
  -v "$(pwd)/$REPORT_DIR":/zap/wrk/:rw \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-api-scan.py -t http://backend:8000/openapi.json -f openapi \
  -J zap-api.json -r zap-api.html -I || true

# Restaurar backend al compose estándar
echo ""
echo "[*] Restaurando contenedor backend al estado de producción..."
docker compose up -d backend >/dev/null 2>&1

# ------------------------------------------------------------------------------
# Consolidación y Tabla Resumen
# ------------------------------------------------------------------------------
echo ""
echo "[*] Generando tabla resumen de hallazgos..."
if command -v python3 >/dev/null 2>&1; then
    python3 scripts/parse_scan_reports.py "$TARGET"
else
    docker run --rm -v "$(pwd)":/work -w /work python:3.12-slim python scripts/parse_scan_reports.py "$TARGET"
fi

echo "================================================================================"
echo "    ESCANEO $TARGET COMPLETADO EXITOSAMENTE"
echo "    Reportes disponibles en: $REPORT_DIR/"
echo "================================================================================"
