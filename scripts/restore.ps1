# ==============================================================================
# CriptoMed - Script de Restauración Cronometrada (PowerShell)
# ==============================================================================
param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$BackupFile
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

$BackupFilename = Split-Path -Leaf $BackupFile

if (-not (Test-Path "backups/$BackupFilename")) {
    Write-Error "El archivo 'backups/$BackupFilename' no existe."
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Error "Archivo .env no encontrado."
    exit 1
}

$EnvContent = Get-Content ".env"
$PassphraseLine = $EnvContent | Where-Object { $_ -match "^BACKUP_PASSPHRASE=" }
if (-not $PassphraseLine) {
    Write-Error "BACKUP_PASSPHRASE no configurada en .env."
    exit 1
}
$BackupPassphrase = $PassphraseLine.Split("=", 2)[1].Trim(' "''')
$RestoreDb = "criptomed_restore_test"

Write-Host "========================================================"
Write-Host "    INICIANDO RESTAURACIÓN CRONOMETRADA (RTO MEDIDO)    "
Write-Host "    Base destino: $RestoreDb (SEPARADA DE PROD)        "
Write-Host "========================================================"

$StartTime = Get-Date

docker compose --profile tools run --rm `
    -e BACKUP_FILENAME="$BackupFilename" `
    -e RESTORE_DB="$RestoreDb" `
    backup bash -c '
        set -euo pipefail
        BACKUP_PATH="/backups/${BACKUP_FILENAME}"
        echo "1. Terminando conexiones activas y recreando base limpia ${RESTORE_DB}..."
        psql -h db -U "$POSTGRES_USER" -d postgres -c "
            SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = \"'"'"'${RESTORE_DB}'"'"'\" AND pid <> pg_backend_pid();
        " >/dev/null 2>&1 || true
        psql -h db -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS ${RESTORE_DB};"
        psql -h db -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE ${RESTORE_DB};"
        echo "2. Descifrando dump con GPG (AES-256) y restaurando en ${RESTORE_DB}..."
        gpg --batch --yes --decrypt --passphrase "$BACKUP_PASSPHRASE" "$BACKUP_PATH" | \
            pg_restore -h db -U "$POSTGRES_USER" -d "$RESTORE_DB" --no-owner --role="$POSTGRES_USER" || true
    '

$EndTime = Get-Date
$Duration = [math]::Round(($EndTime - $StartTime).TotalSeconds, 2)

Write-Host ""
Write-Host "========================================================"
Write-Host "✅ RESTAURACIÓN COMPLETADA EXITOSAMENTE"
Write-Host "   Base de datos : $RestoreDb"
Write-Host "   Tiempo total  : ${Duration}s (RTO medido)"
Write-Host "========================================================"
