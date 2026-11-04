# ==============================================================================
# CriptoMed - Script de Backup de Base de Datos Cifrado (PowerShell)
# ==============================================================================
$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

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

if (-not (Test-Path "backups")) {
    New-Item -ItemType Directory -Path "backups" | Out-Null
}

$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$BackupFilename = "backup_${Timestamp}.dump.gpg"

Write-Host "========================================================"
Write-Host "    INICIANDO BACKUP CIFRADO (NIST SP 800-38D / AES-256)"
Write-Host "========================================================"
Write-Host "Archivo objetivo: backups/$BackupFilename"

$StartTime = Get-Date

docker compose --profile tools run --rm `
    -e BACKUP_FILENAME="$BackupFilename" `
    backup bash -c '
        set -euo pipefail
        BACKUP_PATH="/backups/${BACKUP_FILENAME}"
        echo "📦 Generando dump custom (-Fc) y cifrando con GPG (AES-256)..."
        pg_dump -h db -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" | \
            gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase "$BACKUP_PASSPHRASE" -o "$BACKUP_PATH"
        echo "🧹 Aplicando política de retención (conservar últimos 7)..."
        cd /backups
        ls -t backup_*.dump.gpg 2>/dev/null | tail -n +8 | xargs -r rm -f
    '

$EndTime = Get-Date
$Duration = [math]::Round(($EndTime - $StartTime).TotalSeconds, 2)

$LocalFile = "backups/$BackupFilename"
if (Test-Path $LocalFile) {
    $Size = (Get-Item $LocalFile).Length
    $SizeKB = [math]::Round($Size / 1KB, 2)
    Write-Host ""
    Write-Host "========================================================"
    Write-Host "✅ BACKUP COMPLETADO EXITOSAMENTE"
    Write-Host "   Archivo  : $LocalFile"
    Write-Host "   Tamaño   : $SizeKB KB"
    Write-Host "   Duración : ${Duration}s"
    Write-Host "========================================================"
} else {
    Write-Error "Error: No se encontró el archivo generado en $LocalFile"
    exit 1
}
