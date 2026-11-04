#!/usr/bin/env bash
# ==============================================================================
# CriptoMed - Script de Backup de Base de Datos Cifrado (NIST SP 800-38D / SP 800-57)
# Realiza pg_dump en formato custom (-Fc) y cifra con GPG AES-256 simétrico.
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo "❌ Error: Archivo .env no encontrado en la raíz del proyecto."
  exit 1
fi

# Cargar variables de entorno necesarias desde .env si no están exportadas
if [ -z "${BACKUP_PASSPHRASE:-}" ]; then
  BACKUP_PASSPHRASE=$(grep -E '^BACKUP_PASSPHRASE=' .env | cut -d '=' -f2- | tr -d '\r"')
fi

if [ -z "${BACKUP_PASSPHRASE:-}" ]; then
  echo "❌ Error: BACKUP_PASSPHRASE no está configurada en el entorno ni en .env."
  exit 1
fi

mkdir -p backups

START_TIME=$(date +%s)
TIMESTAMP=$(date +"%Y-%m-%d_%H%M")
BACKUP_FILENAME="backup_${TIMESTAMP}.dump.gpg"

echo "========================================================"
echo "    INICIANDO BACKUP CIFRADO (NIST SP 800-38D / AES-256)"
echo "========================================================"
echo "Archivo objetivo: backups/${BACKUP_FILENAME}"

docker compose --profile tools run --rm \
  -e BACKUP_FILENAME="$BACKUP_FILENAME" \
  backup bash -c '
    set -euo pipefail
    BACKUP_PATH="/backups/${BACKUP_FILENAME}"
    
    echo "📦 Generando dump custom (-Fc) y cifrando con GPG (AES-256)..."
    pg_dump -h db -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" | \
      gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase "$BACKUP_PASSPHRASE" -o "$BACKUP_PATH"
    
    echo "🧹 Aplicando política de retención (conservando últimos 7 backups)..."
    cd /backups
    # Listar ordenados por fecha y eliminar a partir del 8vo más reciente
    ls -t backup_*.dump.gpg 2>/dev/null | tail -n +8 | while read -r old_file; do
      if [ -n "$old_file" ]; then
        echo "   Eliminando backup antiguo: $old_file"
        rm -f "$old_file"
      fi
    done
'

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
LOCAL_FILE="backups/${BACKUP_FILENAME}"

if [ -f "$LOCAL_FILE" ]; then
  SIZE=$(du -h "$LOCAL_FILE" | cut -f1)
  echo ""
  echo "========================================================"
  echo "✅ BACKUP COMPLETADO EXITOSAMENTE"
  echo "   Archivo  : $LOCAL_FILE"
  echo "   Tamaño   : $SIZE"
  echo "   Duración : ${DURATION}s"
  echo "========================================================"
else
  echo "❌ Error: No se encontró el archivo generado en $LOCAL_FILE"
  exit 1
fi
