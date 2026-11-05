#!/bin/bash
# Script de backup automático diario
# Conforme a NIST SP 800-92 (logging) y NIST SP 800-61 (incident response)

set -e

# Configuración
BACKUP_DIR="./backups"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="criptomed_backup_${TIMESTAMP}.sql.gpg"

# Crear directorio de backups si no existe
mkdir -p "$BACKUP_DIR"

echo "[$(date)] Iniciando backup automático..."

# Ejecutar backup desde Docker
docker compose exec -T db pg_dump -U app criptomedschema | \
  gpg --batch --yes --passphrase "$BACKUP_PASSPHRASE" --symmetric \
  --cipher-algo AES256 --compress-algo 1 --s2k-digest-algo SHA256 \
  > "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "[$(date)] Backup exitoso: $BACKUP_FILE"

  # Limpiar backups antiguos
  find "$BACKUP_DIR" -name "criptomed_backup_*.sql.gpg" -mtime +$RETENTION_DAYS -delete
  echo "[$(date)] Backups antiguos (> $RETENTION_DAYS días) eliminados"

  # Verificar integridad del backup
  if gpg --batch --yes --passphrase "$BACKUP_PASSPHRASE" --decrypt "$BACKUP_DIR/$BACKUP_FILE" > /dev/null 2>&1; then
    echo "[$(date)] Verificación de integridad: OK"
  else
    echo "[$(date)] ERROR: Verificación de integridad falló"
    exit 1
  fi
else
  echo "[$(date)] ERROR: Backup falló"
  exit 1
fi

echo "[$(date)] Backup automático completado"
