#!/usr/bin/env bash
# ==============================================================================
# CriptoMed - Script de Restauración Cronometrada (RTO Medido)
# Descifra y restaura un backup GPG AES-256 en la base aislada 'criptomed_restore_test'.
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ $# -lt 1 ]; then
  echo "Uso: $0 <archivo_backup.dump.gpg>"
  echo "Ejemplo: $0 backups/backup_2026-11-04_1430.dump.gpg"
  exit 1
fi

INPUT_FILE="$1"
BACKUP_FILENAME=$(basename "$INPUT_FILE")

if [ ! -f "backups/${BACKUP_FILENAME}" ]; then
  echo "❌ Error: El archivo 'backups/${BACKUP_FILENAME}' no existe."
  exit 1
fi

if [ ! -f .env ]; then
  echo "❌ Error: Archivo .env no encontrado."
  exit 1
fi

if [ -z "${BACKUP_PASSPHRASE:-}" ]; then
  BACKUP_PASSPHRASE=$(grep -E '^BACKUP_PASSPHRASE=' .env | cut -d '=' -f2- | tr -d '\r"')
fi

if [ -z "${BACKUP_PASSPHRASE:-}" ]; then
  echo "❌ Error: BACKUP_PASSPHRASE no configurada."
  exit 1
fi

RESTORE_DB="criptomed_restore_test"

echo "========================================================"
echo "    INICIANDO RESTAURACIÓN CRONOMETRADA (RTO MEDIDO)    "
echo "    Base destino: $RESTORE_DB (SEPARADA DE PROD)       "
echo "========================================================"
echo "Archivo origen: backups/${BACKUP_FILENAME}"

START_TIME=$(date +%s)

docker compose --profile tools run --rm \
  -e BACKUP_FILENAME="$BACKUP_FILENAME" \
  -e RESTORE_DB="$RESTORE_DB" \
  backup bash -c '
    set -euo pipefail
    BACKUP_PATH="/backups/${BACKUP_FILENAME}"
    
    echo "1. Terminando conexiones activas y recreando base limpia ${RESTORE_DB}..."
    psql -h db -U "$POSTGRES_USER" -d postgres -c "
      SELECT pg_terminate_backend(pid) 
      FROM pg_stat_activity 
      WHERE datname = \"'"'"'${RESTORE_DB}'"'"'\" AND pid <> pg_backend_pid();
    " >/dev/null 2>&1 || true
    
    psql -h db -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS ${RESTORE_DB};"
    psql -h db -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE ${RESTORE_DB};"

    echo "2. Descifrando dump con GPG (AES-256) y restaurando en ${RESTORE_DB}..."
    gpg --batch --yes --decrypt --passphrase "$BACKUP_PASSPHRASE" "$BACKUP_PATH" | \
      pg_restore -h db -U "$POSTGRES_USER" -d "$RESTORE_DB" --no-owner --role="$POSTGRES_USER" || true
'

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "========================================================"
echo "✅ RESTAURACIÓN COMPLETADA EXITOSAMENTE"
echo "   Base de datos : $RESTORE_DB"
echo "   Tiempo total  : ${DURATION}s (RTO medido)"
echo "========================================================"
