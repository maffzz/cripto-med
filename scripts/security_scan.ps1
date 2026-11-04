# ==============================================================================
# scripts/security_scan.ps1
# Suite automatizada de escaneo de seguridad multi-herramienta (Fase 2 - Windows).
# ==============================================================================

param (
    [string]$Target = "before"
)

if ($Target -ne "before" -and $Target -ne "after") {
    Write-Host "Uso: .\scripts\security_scan.ps1 [before|after]"
    exit 1
}

$ReportDir = "reports/$Target"
if (!(Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
}

Write-Host "================================================================================"
Write-Host "    INICIANDO ESCANEO DE SEGURIDAD MULTI-HERRAMIENTA: $Target"
Write-Host "    Destino de reportes: $ReportDir/"
Write-Host "================================================================================"

docker compose up -d db backend edge

if (Test-Path "docker-compose.scan.yml") {
    docker compose -f docker-compose.yml -f docker-compose.scan.yml up -d backend
    Start-Sleep -Seconds 3
}

$pwd = (Get-Location).Path

# 1. Bandit
Write-Host "`n>>> [1/8] SAST: Bandit..."
docker run --rm -v "${pwd}:/src" -w /src python:3.12-slim sh -c "pip install --no-cache-dir bandit >/dev/null 2>&1 && bandit -r backend/app backend/scripts -f json -o /src/$ReportDir/bandit.json; bandit -r backend/app backend/scripts -f html -o /src/$ReportDir/bandit.html"

# 2. pip-audit
Write-Host "`n>>> [2/8] SCA: pip-audit..."
docker run --rm -v "${pwd}:/src" -w /src python:3.12-slim sh -c "pip install --no-cache-dir pip-audit >/dev/null 2>&1 && pip-audit -r backend/requirements.txt -f json -o /src/$ReportDir/pip-audit.json"

# 3. npm audit
Write-Host "`n>>> [3/8] SCA: npm audit..."
docker run --rm -v "${pwd}:/repo" -w /repo/frontend node:20-alpine sh -c "npm audit --json > /repo/$ReportDir/npm-audit.json 2>&1"

# 4. Gitleaks
Write-Host "`n>>> [4/8] SECRETOS: Gitleaks..."
docker run --rm -v "${pwd}:/repo" zricethezav/gitleaks:latest detect --source=/repo --report-format=json --report-path=/repo/$ReportDir/gitleaks.json --no-banner --verbose

# 5. Hadolint
Write-Host "`n>>> [5/8] LINT: Hadolint..."
docker run --rm -v "${pwd}:/work" -w /work hadolint/hadolint:latest-alpine hadolint -f json docker/backend/Dockerfile docker/edge/Dockerfile docker/backup/Dockerfile > "$ReportDir/hadolint.json"

# 6. Trivy
Write-Host "`n>>> [6/8] VULNERABILIDADES: Trivy..."
docker run --rm -v "${pwd}:/work" aquasec/trivy:latest fs --format json -o /work/$ReportDir/trivy-fs.json /work
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "${pwd}:/work" aquasec/trivy:latest image --format json -o /work/$ReportDir/trivy-backend.json cripto-med-backend:latest
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "${pwd}:/work" aquasec/trivy:latest image --format json -o /work/$ReportDir/trivy-edge.json cripto-med-edge:latest

# 7. testssl.sh
Write-Host "`n>>> [7/8] TLS: testssl.sh..."
docker run --rm --network cripto-med_app_net -v "${pwd}/$ReportDir:/reports" drwetter/testssl.sh:latest --jsonfile /reports/testssl.json --htmlfile /reports/testssl.html --quiet --warnings off https://edge:8443

# 8. OWASP ZAP
Write-Host "`n>>> [8/8] DAST: OWASP ZAP..."
docker run --rm --network cripto-med_app_net -v "${pwd}/$ReportDir:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://backend:8000 -J zap-baseline.json -r zap-baseline.html -I
docker run --rm --network cripto-med_app_net -v "${pwd}/$ReportDir:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py -t http://backend:8000/openapi.json -f openapi -J zap-api.json -r zap-api.html -I

docker compose up -d backend

Write-Host "`n[*] Generando resumen..."
docker compose run --rm backend python scripts/parse_scan_reports.py "$Target"
